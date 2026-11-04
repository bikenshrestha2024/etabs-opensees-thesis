"""Thread-safe analysis case ledger and live GUI view; no inferred completion."""
import json,time,threading,datetime,re
from pathlib import Path


_CASE_START=re.compile(r'^\[START\]\s+([^:]+):')
_CASE_PROGRESS=re.compile(
    r'^\[PROGRESS\]\s+([^:]+):\s+(\d+)/(\d+)\s+steps,\s+t=([\d.eE+-]+)s')
_CASE_COMPLETE=re.compile(r'^\[OK\]\s+([^:]+):')
_CASE_TRUNCATED=re.compile(r'^\[TRUNCATED\]\s+([^:]+):\s+analyzed\s+([\d.eE+-]+)s\s+of\s+([\d.eE+-]+)s')


class CaseLedger:
 def __init__(self,path,ids):
  self.path=Path(path);self.lock=threading.RLock();self.rows={i:dict(case=i,status='QUEUED',stage='Waiting',elapsed_s=0.) for i in ids};self.save()
 def save(self):
  self.path.parent.mkdir(parents=True,exist_ok=True)
  temp=self.path.with_suffix('.tmp');temp.write_text(json.dumps(dict(updated_at=datetime.datetime.now().astimezone().isoformat(),cases=list(self.rows.values())),indent=2),encoding='utf8');temp.replace(self.path)
 def set(self,key,status,stage):
  with self.lock:
   row=self.rows[key]
   if status in ('RUNNING','PREPARING') and '_start' not in row:row['_start']=time.monotonic()
   row.update(status=status,stage=stage)
   if '_start' in row:row['elapsed_s']=time.monotonic()-row['_start']
   self.save()
 def snapshot(self):
  with self.lock:
   return [dict(r,elapsed_s=time.monotonic()-r['_start'] if r['status'] in ('RUNNING','PREPARING') else r['elapsed_s']) if '_start' in r else dict(r) for r in self.rows.values()]
 def finish_pending(self,reason):
  for key,row in self.rows.items():
   if row['status'] in ('QUEUED','RUNNING','PREPARING'):self.set(key,'NOT COMPLETED',reason)


def update_history_case(ledger,line,current_case=None):
 """Update an LTH/NLTH case from its structured stdout progress messages."""
 if ledger is None:return current_case
 match=_CASE_START.search(line)
 if match:
  case=match.group(1).strip()
  if case in ledger.rows:
   ledger.set(case,'RUNNING','Building model, completing gravity, and preparing transient analysis')
   return case
 match=_CASE_PROGRESS.search(line)
 if match:
  case=match.group(1).strip()
  if case in ledger.rows:
   step,total=int(match.group(2)),int(match.group(3))
   percent=100.*step/total if total else 0.
   ledger.set(case,'RUNNING',
              f'Transient steps {step}/{total} ({percent:.1f}%), physical time {match.group(4)} s')
   return case
 match=_CASE_TRUNCATED.search(line)
 if match:
  case=match.group(1).strip()
  if case in ledger.rows:
   ledger.set(case,'TRUNCATED',
              f'Diagnostic interval {match.group(2)} s of {match.group(3)} s; not a full-record result')
   return None
 match=_CASE_COMPLETE.search(line)
 if match:
  case=match.group(1).strip()
  if case in ledger.rows:
   ledger.set(case,'COMPLETED','Configured record/orientation completed; inspect summary for full-record coverage')
   return None
 return current_case


def panel(parent):
 from tkinter import ttk
 box=ttk.LabelFrame(parent,text='Record / orientation completion (physical-step progress; elapsed is wall time)');box.pack(fill='x',pady=4)
 tree=ttk.Treeview(box,columns=('case','status','stage','elapsed'),show='headings',height=5)
 for c,w in [('case',190),('status',125),('stage',600),('elapsed',100)]:tree.heading(c,text=c);tree.column(c,width=w,stretch=c=='stage')
 scrollbar=ttk.Scrollbar(box,orient='vertical',command=tree.yview);tree.configure(yscrollcommand=scrollbar.set)
 tree.pack(side='left',fill='x',expand=True);scrollbar.pack(side='right',fill='y')
 holder={'ledger':None,'process':None,'cancelled':False}
 def stop():
  holder['cancelled']=True
  proc=holder.get('process')
  if proc is not None and proc.poll() is None:proc.terminate()
  if holder.get('ledger'):holder['ledger'].finish_pending('Stopped by user; no completion claimed')
 ttk.Button(box,text='Stop selected batch',command=stop).pack(anchor='w')
 def tick():
  if not tree.winfo_exists():return
  ledger=holder['ledger']
  if ledger:
   for r in ledger.snapshot():
    vals=(r['case'],r['status'],r['stage'],format(r['elapsed_s'],'.1f')+' s')
    if tree.exists(r['case']):tree.item(r['case'],values=vals)
    else:tree.insert('', 'end',iid=r['case'],values=vals)
  tree.after(1000,tick)
 tick();return holder


def modal_exit_status(cancelled, exit_code):
 """Map subprocess outcome to an honest modal case status.

 An operator-terminated solver may return a nonzero process exit code, but
 the outcome must be CANCELLED (not natural eigenanalysis failure).
 """
 if cancelled:
  return "CANCELLED"
 return "FAILED" if exit_code else "COMPLETED"
