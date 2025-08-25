strategy safe = control:A[] !behavior_shield.Error
saveStrategy("/home/rong/Github/StagedShieldSynthesis/car/shield/safeCar.json",safe)
simulate [<=MAXTIME] { cps_dyn.x, cps_dyn.y, i2d(cps_state.head), cps_dyn.vel, i2d(cps_state.acc) } under safe