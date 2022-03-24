from random import choice
from string import ascii_uppercase, ascii_lowercase, digits
from .models import Fetch
from .settings import CURRENT_RELEASE
from django.conf import settings
from django.http import HttpResponse
from pathlib import Path
from distutils.file_util import copy_file
import os
import time
import subprocess as sp


def random_string_id(x):
    string = (''.join(choice(ascii_lowercase + ascii_uppercase + digits) for i in range(x)))
    return string


def generate_and_check_fetch_id(dest="fetch"):
    fetch_id = random_string_id(16)
    if os.path.isdir(str(settings.MEDIA_ROOT) + '/' + dest + '/' + fetch_id) or Fetch.objects.filter(fetch_id=fetch_id).exists():
        generate_and_check_fetch_id()
    else:
        return fetch_id


def get_id_path(fetch_id, dest="fetch"):
    id_path = str(settings.MEDIA_ROOT) + "/" + dest + "/" + fetch_id + "/"
    print("id_path: ", id_path)
    return id_path


def create_directory(directory):
    if not os.path.exists(directory):
        Path(directory).mkdir(parents=True, exist_ok=False)
    return 0


def rsync_process(species_name, ensembl_version, reference_type, destination):
    # change 'species_name' to fit our needs
    ad_species_name = species_name.strip().lower().replace(" ", "_")

    type_dict = {'gtf': 'gtf',
                 'gff3': 'gff3',
                 'fasta': 'fasta',
                 'fasta_fai': 'fasta'}

    f_type = type_dict[reference_type]

    source = f"rsync://ftp.ensembl.org/ensembl/pub/release-{ensembl_version}/{f_type}/{ad_species_name}/"
    if reference_type == "gtf":
        source = source + f"*.{ensembl_version}.gtf.gz"
    elif reference_type == "gff3":
        source = source + f"*.{ensembl_version}.gff3.gz"
    elif reference_type == "fasta":
        source = source + "dna/*.dna.toplevel.fa.gz"
    elif reference_type == "fasta_fai":
        source = source + "dna_index/*.dna.toplevel.fa.gz.fai"
        
    print("source:", source)

    file = rsync_file(source=source, destination=destination)

    return file


def rsync_file(source, destination):
    # create subprocess command
    command = ['rsync', '-avi', source, destination]

    finished = False

    retries = 0
    
    while not finished:

        process = sp.run(command,
                         stderr=sp.PIPE,
                         stdout=sp.PIPE,
                         shell=False,
                         universal_newlines=True)

        if process.returncode == 0:
            print("File loaded successfully")
            with open("file.txt", "w") as fl:
                print(process.stdout, file=fl)

            with open("file.txt", "r") as fi:
                for line in fi:
                    items = line.split(" ")
                    if items[0] == ">f+++++++++":
                        file_name = items[1].strip()
                        return file_name
        else:
            print("File loading with error code:{0}".format(str(process.returncode)))
            print("out:", process.stdout)
            print("err:", process.stderr)
            if "No such file or directory" in process.stdout or "No such file or directory" in process.stderr:
                print("Something is wrong")
            retries += 1 
            print("retries:", retries)
            if retries >= 50:
                return HttpResponse("There was some kind of error. Please try again later.")
            time.sleep(5)


def download_fetch(fetch_id, file):
    fetch_path = str(settings.MEDIA_ROOT) + "/fetch/" + fetch_id + "/" + file

    fetch_extension = file.split(".")[-1]

    print("extension:", fetch_extension)
    
    if os.path.exists(fetch_path):
        if fetch_extension == "gtf":
            with open(fetch_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(fetch_path)
                return response
        elif fetch_extension == "zip":
            with open(fetch_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/zip")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(fetch_path)
                return response
        elif fetch_extension == "gz":
            with open(fetch_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/gzip")
                response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(fetch_path)
                return response

def get_file_name(fetch_id):
    fetch_path = str(settings.MEDIA_ROOT) + "/fetch/" + fetch_id + "/file.txt" 

    with open(fetch_path, "r") as fi:
                for line in fi:
                    items = line.split(" ")
                    if items[0] == ">f+++++++++":
                        file_name = items[1].strip()
                        return file_name