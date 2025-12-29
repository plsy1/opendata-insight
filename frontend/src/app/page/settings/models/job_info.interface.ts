export interface JobInfo {
  id: string;
  name: string;
  next_run_time: string | null;
  trigger: string;
}