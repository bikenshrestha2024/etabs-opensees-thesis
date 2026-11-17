"""Stage timing associated with every created/changed output, without corrupting CSV schemas."""

__release__ = '134'
import functools,inspect,json,time,traceback
from pathlib import Path
from datetime import datetime,timezone,timedelta
NEPAL=timezone(timedelta(hours=5,minutes=45))
def stamp():return datetime.now(NEPAL).isoformat(timespec='milliseconds')

def _metadata_root(folder):
    """[REF docs/source/components/shared/timing.py.md] Keep generated
    sidecars under a structured metadata folder; leave historic files intact.
    """
    root=Path(folder)/"00_PROCESSING_METADATA"
    if root.is_symlink() or (root/"ARTIFACTS").is_symlink():
        raise ValueError("Linked processing metadata folder refused")
    return root


def _write_metadata(folder, files, metadata):
    root=_metadata_root(folder)
    root.mkdir(parents=True,exist_ok=True)
    records=root/"ARTIFACTS"
    index_path=root/"OUTPUT_TIMING_INDEX_V130.json"
    try:
        index=json.loads(index_path.read_text(encoding="utf-8")) if index_path.is_file() else {}
        if not isinstance(index,dict):
            raise ValueError("Malformed timing index")
    except (OSError,ValueError):
        index={}
    from components.inputs.output_contract import atomic_json
    count=0
    for path in files:
        if path.is_symlink() or not path.is_file():
            continue
        relative=path.relative_to(folder)
        if "00_PROCESSING_METADATA" in relative.parts:
            continue
        child=records/relative.parent/(relative.name+".processing.json")
        if any(p.is_symlink() for p in (child,child.parent,records)):
            raise ValueError("Refusing linked processing metadata target")
        record=dict(metadata,artifact=relative.as_posix(),size_bytes=path.stat().st_size)
        atomic_json(child,record)
        index[relative.as_posix()]=record
        count+=1
    atomic_json(index_path,index)
    log=root/"Processing_Timings_V130.jsonl"
    if log.is_symlink():
        raise ValueError("Refusing linked timing log")
    with log.open("a",encoding="utf-8") as stream:
        stream.write(json.dumps(dict(metadata,artifact_count=count),allow_nan=False)+"\n")
    return count

def _snapshot_derived_files(folder):
    """[REF docs/source/components/shared/timing.py.md]
    Snapshot derived artifacts without relying on wall-clock mtime thresholds.
    """
    found={}
    if not folder or not folder.is_dir():
        return found
    for p in folder.rglob('*'):
        if p.is_symlink() or not p.is_file():
            continue
        rel=p.relative_to(folder)
        if ('00_PROCESSING_METADATA' in rel.parts
                or '__pycache__' in rel.parts
                or p.name.endswith('.processing.json')
                or p.name in ('Processing_Timings_V130.jsonl',
                              'OUTPUT_TIMING_INDEX_V130.json')):
            continue
        try:
            stat=p.stat()
        except FileNotFoundError:
            continue
        found[p]=(stat.st_mtime_ns,stat.st_size)
    return found


def timed_outputs(stage,argument):
    def decorate(function):
        @functools.wraps(function)
        def wrapped(*args,**kwargs):
            bound=inspect.signature(function).bind(*args,**kwargs);bound.apply_defaults();value=bound.arguments.get(argument)
            if isinstance(value,dict):value=value.get('output_dir')
            folder=Path(value).resolve() if value else None
            if folder and (folder.is_file() or (not folder.exists() and folder.suffix)):folder=folder.parent
            before=_snapshot_derived_files(folder)
            started=stamp();clock=time.perf_counter();status='completed';failure=None
            try:return function(*args,**kwargs)
            except BaseException as exc:
                status='failed';failure=f'{type(exc).__name__}: {exc}';raise
            finally:
                elapsed=time.perf_counter()-clock
                metadata=dict(stage=stage,started_at=started,finished_at=stamp(),elapsed_seconds=elapsed,status=status,error=failure,time_scope='Entire named processing stage, not individual file-write latency')
                if folder and folder.exists():
                    try:
                        after=_snapshot_derived_files(folder)
                        files=[p for p,signature in after.items()
                               if before.get(p)!=signature]
                        _write_metadata(folder,files,metadata)
                    except Exception as exc:print(f'[TIMING METADATA ERROR] {stage}: {exc}',flush=True)
                print(f'[TIMING] {stage} | {status} | elapsed={elapsed:.3f} s | start={started} | finish={metadata["finished_at"]}',flush=True)
        return wrapped
    return decorate


class StageTimer:
    def __init__(self,folder,stage):
        self.folder=Path(folder);self.stage=stage;self.clock=time.perf_counter();self.started=stamp();self.finished=False
        self.initial_files = self._artifact_stats()

    def _artifact_stats(self):
        artifacts = {}
        for path in self.folder.glob('*'):
            if (path.is_symlink() or not path.is_file()
                    or path.name.endswith('.processing.json')
                    or path.name.startswith(('OUTPUT_TIMING_INDEX', 'Processing_Timings'))):
                continue
            try:
                info = path.stat()
            except FileNotFoundError:
                continue
            artifacts[path] = (info.st_mtime_ns, info.st_size)
        return artifacts

    def finish(self,status='unconfirmed — inspect solver exit log'):
        if self.finished:return
        self.finished=True;elapsed=time.perf_counter()-self.clock
        data=dict(stage=self.stage,started_at=self.started,finished_at=stamp(),elapsed_seconds=elapsed,status=status,time_scope='Entire processing stage, not individual write latency')
        self.folder.mkdir(parents=True,exist_ok=True)
        files = [path for path, stat in self._artifact_stats().items()
                 if self.initial_files.get(path) != stat]
        _write_metadata(self.folder,files,data)
        print(f'[TIMING] {self.stage} | {status} | elapsed={elapsed:.3f}s | start={self.started} | finish={data["finished_at"]}',flush=True)
