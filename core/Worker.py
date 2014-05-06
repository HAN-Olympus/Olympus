import gearman

""" This is the default worker for Olympus """

gm_worker = gearman.GearmanWorker(['localhost:4730']) # 