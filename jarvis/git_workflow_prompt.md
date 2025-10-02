I worked in this project, called jarvis-streamdeck, using as a base the code from this repository:

https://github.com/abcminiuser/python-elgato-streamdeck

This repository gives me a python interface to interact with the streamdeck device. I simply have added a layer on top of it with actions and the possibility to set different layouts to customize the functionality of the streamdeck. I have now a codebase that is the result from this work. All of it is stored in the jarvis directory.

This repo had the master branch name as it came from the upstream repo. I did not like that, so I changed its name to main.

The README.md in the parent directory has been updated to reflect my contributions to the upstream repo. For now, do not read it.

You have to create a detailed to do list, and create a folder inside jarvis called git_docs where you will write markdown files explaining your complete thought process on how to implement both workflows and the steps that I need to follow to implement these two workflows and achieve the desired results. You will write these markdown files in a way that I can understand them, as I am not very familiar with git. You will also provide me with the exact commands that I need to run in the terminal to achieve these two workflows. They need to be able to complement each other seamlessly.

# Workflow 1: Squash merge dev into main. Show only clean codebase in main branch, and keep extensive commented codebase in dev branch. Keep commit history in dev branch, but show only one clean commit in main branch.

I created a dev branch, where I did all my work. In this branch, I am committing all my changes, but they are very messy, some are experimental, and I have not cleaned them up. However at this point, my repo is almost ready to be pushed, so I need to merge dev into main, and then push main to the remote repo. An important detail, is that I do not want to show my complete history of commits in the dev branch, because it is very messy. I want to have a clean history in main, with only the final versions of the files. So I want to do a squash merge from dev into main. I need you to provide very detailed instructions on how to do this. Consider that you are a computer science professor explaining to a student who is not very familiar with git. I want to be able to do this without making mistakes, so please be very detailed in your instructions.

# Workflow 2: Implement a documentation pipeline that takes comments from the codebase, and generates markdown files that can be deployed to GitHub pages using Quartz. Integrate this pipeline with GitHook and GitHub Actions. Use Docs-as-Code (DaC) principles, single-sourcing, and CI/CD.

I am also using this project as part of my portfolio to show to potential employers. I am applying tomorrow for a position at Google as a Technical writer. Therefore, I need to show principles of code-first, Docs-as-Code (DaC), single-sourcing in my documentation and CI/CD pipeline.

Since my codebase (the jarvis dir) has very extensive comments, I want to clean up the codebase that I will push to GitHub (this is actually part of the workflow 1), and I want to use the extensive comments to generate documentation automatically. I basically want to implement a pipeline that takes the comments from the codebase, and generates markdown files that I can use as documentation. I want to use Quartz to then deploy the markdown files to a static website using GitHub pages. I want to make sure that docstrings, comments, comment blocks, and other relevant information are extracted from the codebase and included in the generated documentation. I want to make sure that the generated documentation is well-structured, easy to navigate, and visually appealing. I also want to make sure that the generated documentation is up-to-date with the codebase, so that whenever I make changes to the codebase, the documentation is updated automatically.

I need to implement this pipeline in a way that is efficient and easy to maintain. I want to use existing tools and frameworks as much as possible, and I want to make sure that the pipeline is well-documented and easy to understand. I also want to make sure that the pipeline is integrated with my CI/CD workflow, so that documentation is generated automatically whenever I push changes to the repository. I want then to integrate this pipeline with GitHook and GitHub Actions.

I want to be able to take the jarvis codebase and strip the codebase of all comments with tags like #EDU, #TOCLEAN, #NOTE,... and then generate markdown files from the comments that I have stripped from the codebase. These markdown files need to get pushed to GitHub pages automatically. I want to be able to do all of this in an automated way, so that I only have to worry about writing code and comments, and the rest is taken care of by the pipeline. I want to be able to trigger the pipeline automatically whenever I push changes to the repository.

An important detail, is that while in GitHub I want to show in main only the cleaned-up codebase, I also want to have the extensive commented codebase available still locally. I do not want to have a duplicate of the codebase, so I want to have a single codebase, but I want to be able to switch between the cleaned up version and the extensive commented version. I want you to consider this when you provide me with the instructions. I think the best would be to create a docs branch, maybe? Just consider that I do not want to lose the extensive commented codebase, but I also do not want to have a duplicate of the codebase. 


# Final Result

I want to be able to push to github only a clean codebase, and locally have the extensive commented codebase. I also want to have a pipeline that takes the comments from the extensive commented codebase, and generates markdown files that can be deployed to GitHub pages using Quartz, all this automatically. I want this pipeline to be integrated with GitHook and GitHub Actions. I want you to provide me with very detailed instructions on how to implement this pipeline. Consider that you are a computer science professor explaining to a student who is not very familiar with git. I want to be able to do this without making mistakes, so please be very detailed in your instructions.

You can also make suggestions on how to better implement these workflows together. Maybe there are better ways to achieve the same result. I am open to suggestions. Think if the tagged comments is actually a good solution. Feel free to modify the githook scripts I had until now. If you need to create new files, do it. Do that only in the jarvis/utils directory. You can also create subdirectories inside jarvis/git_docs if you need to. Just make sure that everything is well organized and easy to understand.

Ignore the jarvis/docs_utils directory for now.

I want you to provide me with very detailed instructions on how to implement this pipeline. Consider that you are a computer science professor explaining to a student who is not very familiar with git. I want to be able to do this without making mistakes, so please be very detailed in your instructions.


