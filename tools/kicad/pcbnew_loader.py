import os
import pathlib
import subprocess
import sys
import site

def add_kicad_to_path():
	if os.name == 'nt':
		import winreg
		aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
		aKey = winreg.OpenKey(aReg, r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KiCad 6.0")
		installPath = pathlib.Path(winreg.QueryValueEx(aKey, "InstallLocation")[0])
		print(f"Found KiCAD at: {installPath}")

		os.add_dll_directory(str(installPath / "bin"))
		os.add_dll_directory(str(installPath / "bin" / "DLLs"))
		site.addsitedir(str(installPath / "bin" / "Lib" / "site-packages"))
	else:
		site.addsitedir("/usr/lib/python3/dist-packages/")

def kicad2step(kicad_pcb_file, step_file, drill_origin=True, grid_origin=False, force=True, no_virtual=False, substitute_models=False, min_distance="0.01mm"):
	assert grid_origin != drill_origin

	if os.name == 'nt':
		import winreg
		aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
		aKey = winreg.OpenKey(aReg, r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KiCad 6.0")
		installPath = pathlib.Path(winreg.QueryValueEx(aKey, "InstallLocation")[0])

		if not os.path.isfile(str(installPath / "bin" / "kicad2step.exe")):
			raise FileNotFoundError(f"kicad2step.exe couln't be found at: {installPath / 'bin' / 'kicad2step.exe'}")

		command = [
			str(installPath / "bin" / "kicad2step.exe"),
			'-o', step_file
		]
		if force:
			command.append("--force")
		if drill_origin:
			command.append("--drill-origin")
		if grid_origin:
			command.append("--grid-origin")
		if no_virtual:
			command.append("--no-virtual")
		if substitute_models:
			command.append("--subst-models")

		command.append("--min-distance")
		command.append(min_distance)

		command.append(kicad_pcb_file)

		subprocess.Popen(command)
