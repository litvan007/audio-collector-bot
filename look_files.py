import os
import logging

def list_files(startpath, log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        )
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        logging.info(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            logging.info(f"{subindent}{f}")

# Пример использования
list_files('.', 'files.log')
