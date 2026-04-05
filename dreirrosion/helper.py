import argparse
import subprocess
import json


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    gen_dep_file_parser = subparsers.add_parser("gen_dep_file")
    gen_dep_file_parser.add_argument("--input")
    gen_dep_file_parser.add_argument("--manifest-path")
    gen_dep_file_parser.add_argument("--depfile")

    args = parser.parse_args()
    print(args)

    output = subprocess.run([
        "cargo",
        "metadata",
        f"--manifest-path={args.manifest_path}",
    ], capture_output=True)
    if output.returncode != 0:
        print(output.stdout.decode("utf-8"))
        print(output.stderr.decode("utf-8"))
        exit(1)

    stdout = output.stdout.decode("utf-8")
    j = json.loads(stdout)

    manifest_paths = []
    for i in j["packages"]:
        id = i["id"]
        if not id.startswith("path+"):
            continue
        manifest_path = i["manifest_path"]
        manifest_paths.append(manifest_path)



    exit(1)


main()
