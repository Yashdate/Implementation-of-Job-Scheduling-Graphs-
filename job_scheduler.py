import tkinter as tk
from tkinter import messagebox, scrolledtext
from collections import defaultdict, deque

# Sample job dependencies: (pre-requisite job, dependent job)
SAMPLE_DEPENDENCIES = [
    ("Setup", "Compile"),
    ("Compile", "Test"),
    ("Compile", "Package"),
    ("Test", "Deploy"),
    ("Package", "Deploy"),
    ("Deploy", "Notify"),
]


class JobSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Scheduling System using Graphs")
        self.root.geometry("700x550")

        self.graph = defaultdict(list)      # adjacency list: job -> dependent jobs
        self.in_degree = defaultdict(int)   # number of pre-requisites of each job
        self.all_nodes = set()              # every job present in the graph

        self.build_gui()
        self.write_output("Welcome! Add dependencies (u must finish before v), "
                          "then click Compute Job Schedule.")

    def build_gui(self):
        input_frame = tk.LabelFrame(self.root, text=" Define Job Dependencies ",
                                    font=("Arial", 11, "bold"), padx=10, pady=10)
        input_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(input_frame, text="Pre-requisite Job (u):").grid(row=0, column=0, sticky="w", pady=5)
        self.u_entry = tk.Entry(input_frame, width=15)
        self.u_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="Dependent Job (v):").grid(row=0, column=2, sticky="w", padx=5)
        self.v_entry = tk.Entry(input_frame, width=15)
        self.v_entry.grid(row=0, column=3, padx=5, pady=5)

        self.add_btn = tk.Button(input_frame, text="Add Dependency", bg="#4CAF50",
                                 fg="white", command=self.add_edge)
        self.add_btn.grid(row=0, column=4, padx=10, pady=5)

        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", padx=15, pady=5)
        self.schedule_btn = tk.Button(action_frame, text="Compute Job Schedule", bg="#2196F3",
                                      fg="white", font=("Arial", 10, "bold"),
                                      command=self.compute_schedule)
        self.schedule_btn.pack(side="left", padx=5)
        tk.Button(action_frame, text="View Graph", command=self.show_graph).pack(side="left", padx=5)
        tk.Button(action_frame, text="Load Sample", command=self.load_sample).pack(side="left", padx=5)
        tk.Button(action_frame, text="Reset", bg="#F44336", fg="white",
                  command=self.reset_graph).pack(side="left", padx=5)

        self.output = scrolledtext.ScrolledText(self.root, height=18, wrap="word",
                                                font=("Consolas", 10))
        self.output.pack(fill="both", expand=True, padx=15, pady=10)

    def write_output(self, message):
        self.output.insert("end", message + "\n")
        self.output.see("end")

    def insert_edge(self, u, v):
        # Directed edge u -> v : job u must be completed before job v
        self.graph[u].append(v)
        self.in_degree[v] += 1
        self.in_degree[u] += 0          # make sure u has an in-degree entry
        self.all_nodes.update([u, v])

    def add_edge(self):
        u = self.u_entry.get().strip()
        v = self.v_entry.get().strip()
        if not u or not v:
            messagebox.showerror("Input Error", "Please enter both job names.")
            return
        if u == v:
            messagebox.showerror("Invalid Dependency", "A job cannot depend on itself.")
            return
        if v in self.graph.get(u, []):
            messagebox.showinfo("Duplicate", f"Dependency {u} -> {v} already exists.")
            return
        self.insert_edge(u, v)
        self.write_output(f"Added dependency: {u} -> {v}")
        self.u_entry.delete(0, "end")
        self.v_entry.delete(0, "end")
        self.u_entry.focus_set()

    def load_sample(self):
        self.reset_graph(silent=True)
        for u, v in SAMPLE_DEPENDENCIES:
            self.insert_edge(u, v)
        self.write_output(f"Loaded sample: {len(self.all_nodes)} jobs, "
                          f"{len(SAMPLE_DEPENDENCIES)} dependencies.")

    def reset_graph(self, silent=False):
        self.graph.clear()
        self.in_degree.clear()
        self.all_nodes.clear()
        self.output.delete("1.0", "end")
        if not silent:
            self.write_output("Graph cleared. Add new job dependencies.")

    def show_graph(self):
        if not self.all_nodes:
            messagebox.showinfo("Graph", "No jobs have been added yet.")
            return
        self.write_output("Adjacency list (job -> dependent jobs):")
        for job in sorted(self.all_nodes):
            targets = ", ".join(sorted(self.graph.get(job, []))) or "-"
            self.write_output(f"  {job} -> {targets}")

    def kahn_schedule(self):
        """Topological sort using Kahn's algorithm (BFS on in-degrees)."""
        indegree = {node: self.in_degree[node] for node in self.all_nodes}
        queue = deque(sorted(n for n in self.all_nodes if indegree[n] == 0))
        order = []
        while queue:
            job = queue.popleft()
            order.append(job)
            for nxt in sorted(self.graph.get(job, [])):
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        return order

    def compute_schedule(self):
        if not self.all_nodes:
            messagebox.showwarning("No Jobs", "Please add at least one dependency first.")
            return
        order = self.kahn_schedule()
        if len(order) != len(self.all_nodes):
            blocked = sorted(self.all_nodes - set(order))
            self.write_output("Cycle detected! Blocked jobs: " + ", ".join(blocked))
            messagebox.showerror("Cycle Detected",
                                 "Circular dependency found. A valid schedule is not possible.")
            return
        self.write_output("Valid job schedule: " + " -> ".join(order))
        self.write_output(f"Total jobs scheduled: {len(order)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = JobSchedulerApp(root)
    root.mainloop()
