
from setuptools import setup
from setuptools.command.build_py import build_py
import os

class my_build_py(build_py):
    def run(self):
	# honor the --dry-run flag
       	if not self.dry_run:
            target_dir = os.path.join(self.build_lib, 'mypkg/media')

            # mkpath is a distutils helper to create directories
            self.mkpath(target_dir)

            with open(os.path.join(target_dir, 'myfile.js'), 'w') as fobj:
                fobj.write(generate_content())

        # distutils uses old-style classes, so no super()
        super(my_build_py, self).run()
	


print os.getcwd()

setup(
    name = "Olympus generated package",
    version = "0.3",
    author = "Stephan Heijl",
	packages = [],
    py_modules=['Olympus.lib.controls.Float', 'Olympus.lib.Log', 'Olympus.lib.Module', 'Olympus.lib.Storage', 'Olympus.lib.controls.Text', 'Olympus.lib.Collection', 'Olympus.modules.acquisition.AcquisitionModule', 'Olympus.lib.controls.Integer', 'Olympus.lib.Config', 'Olympus.lib.StoredObject', 'Olympus.lib.Article', 'Olympus.lib.Singleton', 'Olympus.lib.Control'],
	cmdclass={'build_py': my_build_py}
)		
		