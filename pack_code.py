import os


def pack_project(output_file="contexto.txt"):
    ignore_dirs = {'.git', '.venv', '__pycache__', '.idea', 'build', 'dist'}
    extensions = {'.py', '.ui'}

    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    path = os.path.join(root, file)
                    f.write(f"\n{'=' * 50}\n")
                    f.write(f"FILE: {path}\n")
                    f.write(f"{'=' * 50}\n\n")
                    with open(path, 'r', encoding='utf-8', errors='ignore') as code_file:
                        f.write(code_file.read())
                    f.write("\n")


if __name__ == "__main__":
    pack_project()