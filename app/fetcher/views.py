import os
from django.shortcuts import render, redirect
from .tasks import generate_and_check_fetch_id, get_id_path, create_directory, rsync_process, download_fetch, get_file_name
from .settings import CURRENT_RELEASE, SPECIES_LIST, ENSEMBL_RELEASE_LIST
from .models import Fetch


def reference_fetcher_view(request, *args, **kwargs):
    # get template_name
    template_name = 'fetcher/fetcher.html'

    if request.method == "POST":
        # save user input as variables
        species_name = request.POST.get("species_name")
        ensembl_version = str(request.POST.get("ensembl_version"))
        print("ensembl_version:", ensembl_version)
        reference_type = request.POST.get("selector")

        if species_name.lower() not in SPECIES_LIST:
            # pass
            return redirect('fetcher:missing')

        # if the chosen Ensembl version is not a valid version or no version is provided default to current release
        if ensembl_version not in ENSEMBL_RELEASE_LIST:
            ensembl_version = CURRENT_RELEASE

        if Fetch.objects.filter(species=species_name.strip().lower().replace(" ", "_"),
                                ensembl_version=ensembl_version,reference=reference_type):
            fetch = Fetch.objects.get(
                species=species_name.strip().lower().replace(" ", "_"), 
                ensembl_version=ensembl_version, 
                reference=reference_type
                )

            existing_id = fetch.fetch_id

            print(f'Found existing copy of requested file at fetch_id {existing_id}')
            
            existing_fetch = get_file_name(existing_id)

            return download_fetch(fetch_id=existing_id, file=existing_fetch)

        # generate fetch_id variable
        fetch_id = generate_and_check_fetch_id()

        # get id_path in mediafiles directory
        id_path = get_id_path(fetch_id)

        # create fetch directory
        create_directory(id_path)

        # change to fetch directory
        os.chdir(id_path)

        destination = "."

        file = rsync_process(species_name=species_name, ensembl_version=ensembl_version, reference_type=reference_type,
                             destination=destination)

        print("file: ", file)
        fetch = Fetch(
            fetch_id=fetch_id, 
            species=species_name.strip().lower().replace(" ", "_"), 
            ensembl_version=ensembl_version, 
            reference=reference_type
        )
        fetch.save()

        return download_fetch(fetch_id=fetch_id, file=file)
        
    return render(request, template_name)


def missing_species_view(request, *args, **kwargs):
    # get template_name
    template_name = 'fetcher/missing_species.html'

    return render(request, template_name)


def ensembl_list_view(request, *args, **kwargs):
    # get template_name
    template_name = 'fetcher/species_list.html'

    spec_list = []
    for species in SPECIES_LIST:
        spec_list.append(species.capitalize())

    return render(request, template_name, context={"species_list": spec_list})


def version_list_view(request, *args, **kwargs):
    # get template_name
    template_name = 'fetcher/version_list.html'

    return render(request, template_name, context={"version_list": ENSEMBL_RELEASE_LIST})

