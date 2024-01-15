import subprocess


class DependencyManager:
    def __init__(self):
        self.installed_dependencies = self._get_installed_dependencies()

    def _get_installed_dependencies(self):
        # Use pip to list installed packages
        result = subprocess.run(
            ['pip', 'list'], capture_output=True, text=True)
        installed_packages = [line.split()[0]
                              for line in result.stdout.split('\n')[2:] if line]
        return set(installed_packages)

    def install_dependencies(self, requirements_path):
        with open(requirements_path, 'r') as file:
            required_packages = [line.strip() for line in file if line.strip()]

        for package in required_packages:
            package_name = package.split('==')[0]
            if package_name not in self.installed_dependencies:
                subprocess.run(['pip', 'install', package])
                self.installed_dependencies.add(package_name)
