import json
import toml
import sys


def update_version(new_version):
    # Update version in package.json
    with open("package.json", "r") as f:
        package_data = json.load(f)

    package_data["version"] = new_version

    with open("package.json", "w") as f:
        json.dump(package_data, f, indent=2)
        f.write("\n")  # Ensure newline at end of file

    # Update version in pyproject.toml
    with open("pyproject.toml", "r") as f:
        pyproject_data = toml.load(f)

    pyproject_data["tool"]["semantic_release"]["version"] = new_version

    with open("pyproject.toml", "w") as f:
        toml.dump(pyproject_data, f)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]
    update_version(new_version)
