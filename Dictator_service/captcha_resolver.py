from captcha_solver import CaptchaSolver
solver=CaptchaSolver('browser')
with open('/images/sbi.png','rb') as inp:
	raw_data=inp.read()
print(solver.solve_captcha(raw_data))
  
