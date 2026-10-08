# Job-shop scheduling experiments

A PyQt desktop application for exploring machine/job schedules with simulated annealing and a genetic algorithm. Load an Excel input, choose algorithm parameters, and inspect the resulting schedule in the UI.

[Download a release](https://github.com/omerdikyol/job_optimization/releases)

## Run from source

```sh
git clone https://github.com/omerdikyol/job_optimization.git
cd job_optimization
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python gui.py
```

On Windows, activate with `.venv\Scripts\activate`. A graphical desktop is required. The UI defaults to `Veri.v1.xlsx`; set the input filename to your own workbook and consult [ReadExcel in models.py](models.py) for its expected columns.

## Code map

- [gui.py](gui.py): input selection, parameters, algorithm actions, and results.
- [algorithms.py](algorithms.py): simulated annealing, genetic search, and fitness evaluation.
- [models.py](models.py): jobs, machines, Excel import, and timeline objects.

## Experiment scope

These are exploratory heuristics, not an exact solver or proof of an optimal schedule. Fitness evaluation currently makes stochastic machine choices rather than following every encoded machine-assignment gene, so the displayed results should not be treated as a validated comparison of assignment policies.


## Screenshots

![WhatsApp Image 2023-11-24 at 15 08 22_2fbe0807](https://github.com/omerdikyol/dy_job_optimization/assets/41495154/c6454036-3653-4e1c-9bf3-40dfbb108185)

![WhatsApp Image 2023-11-24 at 15 08 22_d8f3270e](https://github.com/omerdikyol/dy_job_optimization/assets/41495154/2fa7266d-f056-4a68-8b41-0fa05dcee201)
