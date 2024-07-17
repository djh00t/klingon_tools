# [2.0.0](https://github.com/djh00t/klingon_tools/compare/v1.0.0...v2.0.0) (2024-07-17)


* ✨ feat(workflows):Update PR creation logic and add PR title and body generation ([a2715bc](https://github.com/djh00t/klingon_tools/commit/a2715bce89fb38068c8f37ab44f2c195ec30e392))


### BREAKING CHANGES

* Updated PR creation and update process, revised step names.

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0](https://github.com/djh00t/klingon_tools/compare/v0.0.26...v1.0.0) (2024-07-17)


### Bug Fixes

* Adjust commit message formatting in auto-pr workflow ([e14e1be](https://github.com/djh00t/klingon_tools/commit/e14e1be7b18d7d4735cee07b5c8667ec0191c5c1))
* Update GitHub CLI installation in auto-pr workflow ([f5c09f6](https://github.com/djh00t/klingon_tools/commit/f5c09f671c88a0a676b7dceae3c916d2dd24271a))


* 🐛 fix(workflow):Update auto-pr workflow ([59b68cf](https://github.com/djh00t/klingon_tools/commit/59b68cf8ffcb69e30260ca0328a2277ece839cb7))
* ✨ feat(ci): enhance PR creation workflow ([fbc51ba](https://github.com/djh00t/klingon_tools/commit/fbc51ba282e23300fe4d0d2348e74b2a3e2b9340))
* ✨ feat(klingon_tools/git_validate_commit.py): add functions for validating Git ([016f389](https://github.com/djh00t/klingon_tools/commit/016f389f1abd805cd5d85d51e64db085aabfb442))


### Features

* Add auto PR workflow for new branches ([96d369f](https://github.com/djh00t/klingon_tools/commit/96d369fd220d05cf30741840f16ff099b76184a0))
* Add git_push functionality to handle pushing changes to remote ([c5e5b12](https://github.com/djh00t/klingon_tools/commit/c5e5b12958634a463d57d953fbc7f693fbdeac2d))
* Add GitHub Actions workflow for automatic pull requests creation ([a0ed313](https://github.com/djh00t/klingon_tools/commit/a0ed3131427d130ed419555ccfd3a7e153519639))
* Add GitHub CLI installation and commit messages fetching to auto-pr ([fad1e67](https://github.com/djh00t/klingon_tools/commit/fad1e6705bad0127f390495c3eeccaa7cc0de2e2))
* Add signed-off-by information to commit message if not present ([f97e034](https://github.com/djh00t/klingon_tools/commit/f97e0345df4d4ac7e70341d919a626763347857e))
* **ci:** Add workflow_dispatch event trigger in GitHub Actions workflow ([db4eb2e](https://github.com/djh00t/klingon_tools/commit/db4eb2e05a2b037e471653db5da229dd42e27d75))
* **git_tools:** Add commit message validation before pushing changes ([be5b2c4](https://github.com/djh00t/klingon_tools/commit/be5b2c4cc8806e6e2a5cbc9a9fa4db390231dc8e))
* **git_user_info:** add functionality to retrieve user's name and email from ([ec8e1e7](https://github.com/djh00t/klingon_tools/commit/ec8e1e76e25ffe7aa1a8b385f43d827eb80b1262))
* **git:** add signed-off-by information to commit messages ([a899489](https://github.com/djh00t/klingon_tools/commit/a899489b59f64730fd9fe6be1d8f62e819c6747f))
* **git:** Push new branch upstream if necessary ([e5f3d92](https://github.com/djh00t/klingon_tools/commit/e5f3d92b5bb77059a480a115c056f756a8a55de9))
* improve PR title generation and workflow automation ([#49](https://github.com/djh00t/klingon_tools/issues/49)) ([f40c445](https://github.com/djh00t/klingon_tools/commit/f40c4450fe7ef4bf0eae9bc4f2a1bddaf1f511a3))
* **klingon_tools:** Add function to retrieve git user info ([cbb52c9](https://github.com/djh00t/klingon_tools/commit/cbb52c99e3c920398b5c8b33ed329b9a4c52751e))
* **klingon_tools:** Add git_validate_commit.py to validate commit messages ([2c29bb0](https://github.com/djh00t/klingon_tools/commit/2c29bb0feb864fdf202b223cc3bc5c533dbdd659))
* **openai:** Add get_git_user_info function call and Signed-off-by footer ([dab7b1b](https://github.com/djh00t/klingon_tools/commit/dab7b1b47c2121ea8564cf221c0c3a29c920f37c))
* **push:** add global repo variable in main function ([57d815c](https://github.com/djh00t/klingon_tools/commit/57d815cf81fcb0f4f5563309b134eacc265bbc33))
* **push:** import validate_commit_messages function in git_tools.py ([1ddb015](https://github.com/djh00t/klingon_tools/commit/1ddb015c03daeab2e1251191262e7c7fb8f2d878))
* Update commit message generation in `openai_tools.py` ([0974840](https://github.com/djh00t/klingon_tools/commit/0974840a0e35e6c1ef9134f643565b4ebd317d5c))
* Update git_tools.py with commit message validation and generation logic ([c0e0b62](https://github.com/djh00t/klingon_tools/commit/c0e0b6275838b8da194057e70fc6642f251c4b78))
* Update git_validate_commit.py to include OpenAI commit message ([73b7124](https://github.com/djh00t/klingon_tools/commit/73b712494f08c7962c04fc17945a6ca7ce1d6359))
* Update pull request creation command to include mention of actor ([eb0f2f7](https://github.com/djh00t/klingon_tools/commit/eb0f2f79d5befdf333ffd2d643270bcb225d03e7))


### BREAKING CHANGES

* This commit modifies the auto-pr workflow behavior.

Signed-off-by: David Hooton <david@hooton.org>
* This commit modifies the PR creation process to ensure single
PR creation per branch.

Signed-off-by: David Hooton <david@hooton.org>
* These changes introduce new functions and enhance commit
message validation capabilities.

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0-release.1](https://github.com/djh00t/klingon_tools/compare/v0.0.26...v1.0.0-release.1) (2024-07-17)


### Bug Fixes

* Adjust commit message formatting in auto-pr workflow ([e14e1be](https://github.com/djh00t/klingon_tools/commit/e14e1be7b18d7d4735cee07b5c8667ec0191c5c1))
* Update GitHub CLI installation in auto-pr workflow ([f5c09f6](https://github.com/djh00t/klingon_tools/commit/f5c09f671c88a0a676b7dceae3c916d2dd24271a))


* 🐛 fix(workflow):Update auto-pr workflow ([59b68cf](https://github.com/djh00t/klingon_tools/commit/59b68cf8ffcb69e30260ca0328a2277ece839cb7))
* ✨ feat(ci): enhance PR creation workflow ([fbc51ba](https://github.com/djh00t/klingon_tools/commit/fbc51ba282e23300fe4d0d2348e74b2a3e2b9340))
* ✨ feat(klingon_tools/git_validate_commit.py): add functions for validating Git ([016f389](https://github.com/djh00t/klingon_tools/commit/016f389f1abd805cd5d85d51e64db085aabfb442))


### Features

* Add auto PR workflow for new branches ([96d369f](https://github.com/djh00t/klingon_tools/commit/96d369fd220d05cf30741840f16ff099b76184a0))
* Add git_push functionality to handle pushing changes to remote ([c5e5b12](https://github.com/djh00t/klingon_tools/commit/c5e5b12958634a463d57d953fbc7f693fbdeac2d))
* Add GitHub Actions workflow for automatic pull requests creation ([a0ed313](https://github.com/djh00t/klingon_tools/commit/a0ed3131427d130ed419555ccfd3a7e153519639))
* Add GitHub CLI installation and commit messages fetching to auto-pr ([fad1e67](https://github.com/djh00t/klingon_tools/commit/fad1e6705bad0127f390495c3eeccaa7cc0de2e2))
* Add signed-off-by information to commit message if not present ([f97e034](https://github.com/djh00t/klingon_tools/commit/f97e0345df4d4ac7e70341d919a626763347857e))
* **ci:** Add workflow_dispatch event trigger in GitHub Actions workflow ([db4eb2e](https://github.com/djh00t/klingon_tools/commit/db4eb2e05a2b037e471653db5da229dd42e27d75))
* **git_tools:** Add commit message validation before pushing changes ([be5b2c4](https://github.com/djh00t/klingon_tools/commit/be5b2c4cc8806e6e2a5cbc9a9fa4db390231dc8e))
* **git_user_info:** add functionality to retrieve user's name and email from ([ec8e1e7](https://github.com/djh00t/klingon_tools/commit/ec8e1e76e25ffe7aa1a8b385f43d827eb80b1262))
* **git:** add signed-off-by information to commit messages ([a899489](https://github.com/djh00t/klingon_tools/commit/a899489b59f64730fd9fe6be1d8f62e819c6747f))
* **git:** Push new branch upstream if necessary ([e5f3d92](https://github.com/djh00t/klingon_tools/commit/e5f3d92b5bb77059a480a115c056f756a8a55de9))
* improve PR title generation and workflow automation ([#49](https://github.com/djh00t/klingon_tools/issues/49)) ([f40c445](https://github.com/djh00t/klingon_tools/commit/f40c4450fe7ef4bf0eae9bc4f2a1bddaf1f511a3))
* **klingon_tools:** Add function to retrieve git user info ([cbb52c9](https://github.com/djh00t/klingon_tools/commit/cbb52c99e3c920398b5c8b33ed329b9a4c52751e))
* **klingon_tools:** Add git_validate_commit.py to validate commit messages ([2c29bb0](https://github.com/djh00t/klingon_tools/commit/2c29bb0feb864fdf202b223cc3bc5c533dbdd659))
* **openai:** Add get_git_user_info function call and Signed-off-by footer ([dab7b1b](https://github.com/djh00t/klingon_tools/commit/dab7b1b47c2121ea8564cf221c0c3a29c920f37c))
* **push:** add global repo variable in main function ([57d815c](https://github.com/djh00t/klingon_tools/commit/57d815cf81fcb0f4f5563309b134eacc265bbc33))
* **push:** import validate_commit_messages function in git_tools.py ([1ddb015](https://github.com/djh00t/klingon_tools/commit/1ddb015c03daeab2e1251191262e7c7fb8f2d878))
* Update commit message generation in `openai_tools.py` ([0974840](https://github.com/djh00t/klingon_tools/commit/0974840a0e35e6c1ef9134f643565b4ebd317d5c))
* Update git_tools.py with commit message validation and generation logic ([c0e0b62](https://github.com/djh00t/klingon_tools/commit/c0e0b6275838b8da194057e70fc6642f251c4b78))
* Update git_validate_commit.py to include OpenAI commit message ([73b7124](https://github.com/djh00t/klingon_tools/commit/73b712494f08c7962c04fc17945a6ca7ce1d6359))
* Update pull request creation command to include mention of actor ([eb0f2f7](https://github.com/djh00t/klingon_tools/commit/eb0f2f79d5befdf333ffd2d643270bcb225d03e7))


### BREAKING CHANGES

* This commit modifies the auto-pr workflow behavior.

Signed-off-by: David Hooton <david@hooton.org>
* This commit modifies the PR creation process to ensure single
PR creation per branch.

Signed-off-by: David Hooton <david@hooton.org>
* These changes introduce new functions and enhance commit
message validation capabilities.

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0-release.1](https://github.com/djh00t/klingon_tools/compare/v0.0.26...v1.0.0-release.1) (2024-07-17)


### Bug Fixes

* Adjust commit message formatting in auto-pr workflow ([e14e1be](https://github.com/djh00t/klingon_tools/commit/e14e1be7b18d7d4735cee07b5c8667ec0191c5c1))
* Update GitHub CLI installation in auto-pr workflow ([f5c09f6](https://github.com/djh00t/klingon_tools/commit/f5c09f671c88a0a676b7dceae3c916d2dd24271a))


* 🐛 fix(workflow):Update auto-pr workflow ([59b68cf](https://github.com/djh00t/klingon_tools/commit/59b68cf8ffcb69e30260ca0328a2277ece839cb7))
* ✨ feat(ci): enhance PR creation workflow ([fbc51ba](https://github.com/djh00t/klingon_tools/commit/fbc51ba282e23300fe4d0d2348e74b2a3e2b9340))
* ✨ feat(klingon_tools/git_validate_commit.py): add functions for validating Git ([016f389](https://github.com/djh00t/klingon_tools/commit/016f389f1abd805cd5d85d51e64db085aabfb442))


### Features

* Add auto PR workflow for new branches ([96d369f](https://github.com/djh00t/klingon_tools/commit/96d369fd220d05cf30741840f16ff099b76184a0))
* Add git_push functionality to handle pushing changes to remote ([c5e5b12](https://github.com/djh00t/klingon_tools/commit/c5e5b12958634a463d57d953fbc7f693fbdeac2d))
* Add GitHub Actions workflow for automatic pull requests creation ([a0ed313](https://github.com/djh00t/klingon_tools/commit/a0ed3131427d130ed419555ccfd3a7e153519639))
* Add GitHub CLI installation and commit messages fetching to auto-pr ([fad1e67](https://github.com/djh00t/klingon_tools/commit/fad1e6705bad0127f390495c3eeccaa7cc0de2e2))
* Add signed-off-by information to commit message if not present ([f97e034](https://github.com/djh00t/klingon_tools/commit/f97e0345df4d4ac7e70341d919a626763347857e))
* **ci:** Add workflow_dispatch event trigger in GitHub Actions workflow ([db4eb2e](https://github.com/djh00t/klingon_tools/commit/db4eb2e05a2b037e471653db5da229dd42e27d75))
* **git_tools:** Add commit message validation before pushing changes ([be5b2c4](https://github.com/djh00t/klingon_tools/commit/be5b2c4cc8806e6e2a5cbc9a9fa4db390231dc8e))
* **git_user_info:** add functionality to retrieve user's name and email from ([ec8e1e7](https://github.com/djh00t/klingon_tools/commit/ec8e1e76e25ffe7aa1a8b385f43d827eb80b1262))
* **git:** add signed-off-by information to commit messages ([a899489](https://github.com/djh00t/klingon_tools/commit/a899489b59f64730fd9fe6be1d8f62e819c6747f))
* **git:** Push new branch upstream if necessary ([e5f3d92](https://github.com/djh00t/klingon_tools/commit/e5f3d92b5bb77059a480a115c056f756a8a55de9))
* improve PR title generation and workflow automation ([#49](https://github.com/djh00t/klingon_tools/issues/49)) ([f40c445](https://github.com/djh00t/klingon_tools/commit/f40c4450fe7ef4bf0eae9bc4f2a1bddaf1f511a3))
* **klingon_tools:** Add function to retrieve git user info ([cbb52c9](https://github.com/djh00t/klingon_tools/commit/cbb52c99e3c920398b5c8b33ed329b9a4c52751e))
* **klingon_tools:** Add git_validate_commit.py to validate commit messages ([2c29bb0](https://github.com/djh00t/klingon_tools/commit/2c29bb0feb864fdf202b223cc3bc5c533dbdd659))
* **openai:** Add get_git_user_info function call and Signed-off-by footer ([dab7b1b](https://github.com/djh00t/klingon_tools/commit/dab7b1b47c2121ea8564cf221c0c3a29c920f37c))
* **push:** add global repo variable in main function ([57d815c](https://github.com/djh00t/klingon_tools/commit/57d815cf81fcb0f4f5563309b134eacc265bbc33))
* **push:** import validate_commit_messages function in git_tools.py ([1ddb015](https://github.com/djh00t/klingon_tools/commit/1ddb015c03daeab2e1251191262e7c7fb8f2d878))
* Update commit message generation in `openai_tools.py` ([0974840](https://github.com/djh00t/klingon_tools/commit/0974840a0e35e6c1ef9134f643565b4ebd317d5c))
* Update git_tools.py with commit message validation and generation logic ([c0e0b62](https://github.com/djh00t/klingon_tools/commit/c0e0b6275838b8da194057e70fc6642f251c4b78))
* Update git_validate_commit.py to include OpenAI commit message ([73b7124](https://github.com/djh00t/klingon_tools/commit/73b712494f08c7962c04fc17945a6ca7ce1d6359))
* Update pull request creation command to include mention of actor ([eb0f2f7](https://github.com/djh00t/klingon_tools/commit/eb0f2f79d5befdf333ffd2d643270bcb225d03e7))


### BREAKING CHANGES

* This commit modifies the auto-pr workflow behavior.

Signed-off-by: David Hooton <david@hooton.org>
* This commit modifies the PR creation process to ensure single
PR creation per branch.

Signed-off-by: David Hooton <david@hooton.org>
* These changes introduce new functions and enhance commit
message validation capabilities.

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0-release.1](https://github.com/djh00t/klingon_tools/compare/v0.0.26...v1.0.0-release.1) (2024-07-17)


### Bug Fixes

* Adjust commit message formatting in auto-pr workflow ([e14e1be](https://github.com/djh00t/klingon_tools/commit/e14e1be7b18d7d4735cee07b5c8667ec0191c5c1))
* Update GitHub CLI installation in auto-pr workflow ([f5c09f6](https://github.com/djh00t/klingon_tools/commit/f5c09f671c88a0a676b7dceae3c916d2dd24271a))


* 🐛 fix(workflow):Update auto-pr workflow ([59b68cf](https://github.com/djh00t/klingon_tools/commit/59b68cf8ffcb69e30260ca0328a2277ece839cb7))
* ✨ feat(ci): enhance PR creation workflow ([fbc51ba](https://github.com/djh00t/klingon_tools/commit/fbc51ba282e23300fe4d0d2348e74b2a3e2b9340))
* ✨ feat(klingon_tools/git_validate_commit.py): add functions for validating Git ([016f389](https://github.com/djh00t/klingon_tools/commit/016f389f1abd805cd5d85d51e64db085aabfb442))


### Features

* Add auto PR workflow for new branches ([96d369f](https://github.com/djh00t/klingon_tools/commit/96d369fd220d05cf30741840f16ff099b76184a0))
* Add git_push functionality to handle pushing changes to remote ([c5e5b12](https://github.com/djh00t/klingon_tools/commit/c5e5b12958634a463d57d953fbc7f693fbdeac2d))
* Add GitHub Actions workflow for automatic pull requests creation ([a0ed313](https://github.com/djh00t/klingon_tools/commit/a0ed3131427d130ed419555ccfd3a7e153519639))
* Add GitHub CLI installation and commit messages fetching to auto-pr ([fad1e67](https://github.com/djh00t/klingon_tools/commit/fad1e6705bad0127f390495c3eeccaa7cc0de2e2))
* Add signed-off-by information to commit message if not present ([f97e034](https://github.com/djh00t/klingon_tools/commit/f97e0345df4d4ac7e70341d919a626763347857e))
* **ci:** Add workflow_dispatch event trigger in GitHub Actions workflow ([db4eb2e](https://github.com/djh00t/klingon_tools/commit/db4eb2e05a2b037e471653db5da229dd42e27d75))
* **git_tools:** Add commit message validation before pushing changes ([be5b2c4](https://github.com/djh00t/klingon_tools/commit/be5b2c4cc8806e6e2a5cbc9a9fa4db390231dc8e))
* **git_user_info:** add functionality to retrieve user's name and email from ([ec8e1e7](https://github.com/djh00t/klingon_tools/commit/ec8e1e76e25ffe7aa1a8b385f43d827eb80b1262))
* **git:** add signed-off-by information to commit messages ([a899489](https://github.com/djh00t/klingon_tools/commit/a899489b59f64730fd9fe6be1d8f62e819c6747f))
* **git:** Push new branch upstream if necessary ([e5f3d92](https://github.com/djh00t/klingon_tools/commit/e5f3d92b5bb77059a480a115c056f756a8a55de9))
* improve PR title generation and workflow automation ([#49](https://github.com/djh00t/klingon_tools/issues/49)) ([f40c445](https://github.com/djh00t/klingon_tools/commit/f40c4450fe7ef4bf0eae9bc4f2a1bddaf1f511a3))
* **klingon_tools:** Add function to retrieve git user info ([cbb52c9](https://github.com/djh00t/klingon_tools/commit/cbb52c99e3c920398b5c8b33ed329b9a4c52751e))
* **klingon_tools:** Add git_validate_commit.py to validate commit messages ([2c29bb0](https://github.com/djh00t/klingon_tools/commit/2c29bb0feb864fdf202b223cc3bc5c533dbdd659))
* **openai:** Add get_git_user_info function call and Signed-off-by footer ([dab7b1b](https://github.com/djh00t/klingon_tools/commit/dab7b1b47c2121ea8564cf221c0c3a29c920f37c))
* **push:** add global repo variable in main function ([57d815c](https://github.com/djh00t/klingon_tools/commit/57d815cf81fcb0f4f5563309b134eacc265bbc33))
* **push:** import validate_commit_messages function in git_tools.py ([1ddb015](https://github.com/djh00t/klingon_tools/commit/1ddb015c03daeab2e1251191262e7c7fb8f2d878))
* Update commit message generation in `openai_tools.py` ([0974840](https://github.com/djh00t/klingon_tools/commit/0974840a0e35e6c1ef9134f643565b4ebd317d5c))
* Update git_tools.py with commit message validation and generation logic ([c0e0b62](https://github.com/djh00t/klingon_tools/commit/c0e0b6275838b8da194057e70fc6642f251c4b78))
* Update git_validate_commit.py to include OpenAI commit message ([73b7124](https://github.com/djh00t/klingon_tools/commit/73b712494f08c7962c04fc17945a6ca7ce1d6359))
* Update pull request creation command to include mention of actor ([eb0f2f7](https://github.com/djh00t/klingon_tools/commit/eb0f2f79d5befdf333ffd2d643270bcb225d03e7))


### BREAKING CHANGES

* This commit modifies the auto-pr workflow behavior.

Signed-off-by: David Hooton <david@hooton.org>
* This commit modifies the PR creation process to ensure single
PR creation per branch.

Signed-off-by: David Hooton <david@hooton.org>
* These changes introduce new functions and enhance commit
message validation capabilities.

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0-release.1](https://github.com/djh00t/klingon_tools/compare/v0.0.26...v1.0.0-release.1) (2024-07-05)


### Bug Fixes

* Adjust commit message formatting in auto-pr workflow ([e14e1be](https://github.com/djh00t/klingon_tools/commit/e14e1be7b18d7d4735cee07b5c8667ec0191c5c1))
* Update GitHub CLI installation in auto-pr workflow ([f5c09f6](https://github.com/djh00t/klingon_tools/commit/f5c09f671c88a0a676b7dceae3c916d2dd24271a))


* 🐛 fix(workflow):Update auto-pr workflow ([59b68cf](https://github.com/djh00t/klingon_tools/commit/59b68cf8ffcb69e30260ca0328a2277ece839cb7))
* ✨ feat(ci): enhance PR creation workflow ([fbc51ba](https://github.com/djh00t/klingon_tools/commit/fbc51ba282e23300fe4d0d2348e74b2a3e2b9340))
* ✨ feat(klingon_tools/git_validate_commit.py): add functions for validating Git ([016f389](https://github.com/djh00t/klingon_tools/commit/016f389f1abd805cd5d85d51e64db085aabfb442))


### Features

* Add auto PR workflow for new branches ([96d369f](https://github.com/djh00t/klingon_tools/commit/96d369fd220d05cf30741840f16ff099b76184a0))
* Add git_push functionality to handle pushing changes to remote ([c5e5b12](https://github.com/djh00t/klingon_tools/commit/c5e5b12958634a463d57d953fbc7f693fbdeac2d))
* Add GitHub Actions workflow for automatic pull requests creation ([a0ed313](https://github.com/djh00t/klingon_tools/commit/a0ed3131427d130ed419555ccfd3a7e153519639))
* Add GitHub CLI installation and commit messages fetching to auto-pr ([fad1e67](https://github.com/djh00t/klingon_tools/commit/fad1e6705bad0127f390495c3eeccaa7cc0de2e2))
* Add signed-off-by information to commit message if not present ([f97e034](https://github.com/djh00t/klingon_tools/commit/f97e0345df4d4ac7e70341d919a626763347857e))
* **ci:** Add workflow_dispatch event trigger in GitHub Actions workflow ([db4eb2e](https://github.com/djh00t/klingon_tools/commit/db4eb2e05a2b037e471653db5da229dd42e27d75))
* **git_tools:** Add commit message validation before pushing changes ([be5b2c4](https://github.com/djh00t/klingon_tools/commit/be5b2c4cc8806e6e2a5cbc9a9fa4db390231dc8e))
* **git_user_info:** add functionality to retrieve user's name and email from ([ec8e1e7](https://github.com/djh00t/klingon_tools/commit/ec8e1e76e25ffe7aa1a8b385f43d827eb80b1262))
* **git:** add signed-off-by information to commit messages ([a899489](https://github.com/djh00t/klingon_tools/commit/a899489b59f64730fd9fe6be1d8f62e819c6747f))
* **git:** Push new branch upstream if necessary ([e5f3d92](https://github.com/djh00t/klingon_tools/commit/e5f3d92b5bb77059a480a115c056f756a8a55de9))
* improve PR title generation and workflow automation ([#49](https://github.com/djh00t/klingon_tools/issues/49)) ([f40c445](https://github.com/djh00t/klingon_tools/commit/f40c4450fe7ef4bf0eae9bc4f2a1bddaf1f511a3))
* **klingon_tools:** Add function to retrieve git user info ([cbb52c9](https://github.com/djh00t/klingon_tools/commit/cbb52c99e3c920398b5c8b33ed329b9a4c52751e))
* **klingon_tools:** Add git_validate_commit.py to validate commit messages ([2c29bb0](https://github.com/djh00t/klingon_tools/commit/2c29bb0feb864fdf202b223cc3bc5c533dbdd659))
* **openai:** Add get_git_user_info function call and Signed-off-by footer ([dab7b1b](https://github.com/djh00t/klingon_tools/commit/dab7b1b47c2121ea8564cf221c0c3a29c920f37c))
* **push:** add global repo variable in main function ([57d815c](https://github.com/djh00t/klingon_tools/commit/57d815cf81fcb0f4f5563309b134eacc265bbc33))
* **push:** import validate_commit_messages function in git_tools.py ([1ddb015](https://github.com/djh00t/klingon_tools/commit/1ddb015c03daeab2e1251191262e7c7fb8f2d878))
* Update commit message generation in `openai_tools.py` ([0974840](https://github.com/djh00t/klingon_tools/commit/0974840a0e35e6c1ef9134f643565b4ebd317d5c))
* Update git_tools.py with commit message validation and generation logic ([c0e0b62](https://github.com/djh00t/klingon_tools/commit/c0e0b6275838b8da194057e70fc6642f251c4b78))
* Update git_validate_commit.py to include OpenAI commit message ([73b7124](https://github.com/djh00t/klingon_tools/commit/73b712494f08c7962c04fc17945a6ca7ce1d6359))
* Update pull request creation command to include mention of actor ([eb0f2f7](https://github.com/djh00t/klingon_tools/commit/eb0f2f79d5befdf333ffd2d643270bcb225d03e7))


### BREAKING CHANGES

* This commit modifies the auto-pr workflow behavior.

Signed-off-by: David Hooton <david@hooton.org>
* This commit modifies the PR creation process to ensure single
PR creation per branch.

Signed-off-by: David Hooton <david@hooton.org>
* These changes introduce new functions and enhance commit
message validation capabilities.

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0-release.1](https://github.com/djh00t/klingon_tools/compare/v0.0.26...v1.0.0-release.1) (2024-07-05)


### Bug Fixes

* Adjust commit message formatting in auto-pr workflow ([e14e1be](https://github.com/djh00t/klingon_tools/commit/e14e1be7b18d7d4735cee07b5c8667ec0191c5c1))
* Update GitHub CLI installation in auto-pr workflow ([f5c09f6](https://github.com/djh00t/klingon_tools/commit/f5c09f671c88a0a676b7dceae3c916d2dd24271a))


* 🐛 fix(workflow):Update auto-pr workflow ([59b68cf](https://github.com/djh00t/klingon_tools/commit/59b68cf8ffcb69e30260ca0328a2277ece839cb7))
* ✨ feat(ci): enhance PR creation workflow ([fbc51ba](https://github.com/djh00t/klingon_tools/commit/fbc51ba282e23300fe4d0d2348e74b2a3e2b9340))
* ✨ feat(klingon_tools/git_validate_commit.py): add functions for validating Git ([016f389](https://github.com/djh00t/klingon_tools/commit/016f389f1abd805cd5d85d51e64db085aabfb442))


### Features

* Add auto PR workflow for new branches ([96d369f](https://github.com/djh00t/klingon_tools/commit/96d369fd220d05cf30741840f16ff099b76184a0))
* Add git_push functionality to handle pushing changes to remote ([c5e5b12](https://github.com/djh00t/klingon_tools/commit/c5e5b12958634a463d57d953fbc7f693fbdeac2d))
* Add GitHub Actions workflow for automatic pull requests creation ([a0ed313](https://github.com/djh00t/klingon_tools/commit/a0ed3131427d130ed419555ccfd3a7e153519639))
* Add GitHub CLI installation and commit messages fetching to auto-pr ([fad1e67](https://github.com/djh00t/klingon_tools/commit/fad1e6705bad0127f390495c3eeccaa7cc0de2e2))
* Add signed-off-by information to commit message if not present ([f97e034](https://github.com/djh00t/klingon_tools/commit/f97e0345df4d4ac7e70341d919a626763347857e))
* **ci:** Add workflow_dispatch event trigger in GitHub Actions workflow ([db4eb2e](https://github.com/djh00t/klingon_tools/commit/db4eb2e05a2b037e471653db5da229dd42e27d75))
* **git_tools:** Add commit message validation before pushing changes ([be5b2c4](https://github.com/djh00t/klingon_tools/commit/be5b2c4cc8806e6e2a5cbc9a9fa4db390231dc8e))
* **git_user_info:** add functionality to retrieve user's name and email from ([ec8e1e7](https://github.com/djh00t/klingon_tools/commit/ec8e1e76e25ffe7aa1a8b385f43d827eb80b1262))
* **git:** add signed-off-by information to commit messages ([a899489](https://github.com/djh00t/klingon_tools/commit/a899489b59f64730fd9fe6be1d8f62e819c6747f))
* **git:** Push new branch upstream if necessary ([e5f3d92](https://github.com/djh00t/klingon_tools/commit/e5f3d92b5bb77059a480a115c056f756a8a55de9))
* improve PR title generation and workflow automation ([#49](https://github.com/djh00t/klingon_tools/issues/49)) ([f40c445](https://github.com/djh00t/klingon_tools/commit/f40c4450fe7ef4bf0eae9bc4f2a1bddaf1f511a3))
* **klingon_tools:** Add function to retrieve git user info ([cbb52c9](https://github.com/djh00t/klingon_tools/commit/cbb52c99e3c920398b5c8b33ed329b9a4c52751e))
* **klingon_tools:** Add git_validate_commit.py to validate commit messages ([2c29bb0](https://github.com/djh00t/klingon_tools/commit/2c29bb0feb864fdf202b223cc3bc5c533dbdd659))
* **openai:** Add get_git_user_info function call and Signed-off-by footer ([dab7b1b](https://github.com/djh00t/klingon_tools/commit/dab7b1b47c2121ea8564cf221c0c3a29c920f37c))
* **push:** add global repo variable in main function ([57d815c](https://github.com/djh00t/klingon_tools/commit/57d815cf81fcb0f4f5563309b134eacc265bbc33))
* **push:** import validate_commit_messages function in git_tools.py ([1ddb015](https://github.com/djh00t/klingon_tools/commit/1ddb015c03daeab2e1251191262e7c7fb8f2d878))
* Update commit message generation in `openai_tools.py` ([0974840](https://github.com/djh00t/klingon_tools/commit/0974840a0e35e6c1ef9134f643565b4ebd317d5c))
* Update git_tools.py with commit message validation and generation logic ([c0e0b62](https://github.com/djh00t/klingon_tools/commit/c0e0b6275838b8da194057e70fc6642f251c4b78))
* Update git_validate_commit.py to include OpenAI commit message ([73b7124](https://github.com/djh00t/klingon_tools/commit/73b712494f08c7962c04fc17945a6ca7ce1d6359))
* Update pull request creation command to include mention of actor ([eb0f2f7](https://github.com/djh00t/klingon_tools/commit/eb0f2f79d5befdf333ffd2d643270bcb225d03e7))


### BREAKING CHANGES

* This commit modifies the auto-pr workflow behavior.

Signed-off-by: David Hooton <david@hooton.org>
* This commit modifies the PR creation process to ensure single
PR creation per branch.

Signed-off-by: David Hooton <david@hooton.org>
* These changes introduce new functions and enhance commit
message validation capabilities.

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0-release.1](https://github.com/djh00t/klingon_tools/compare/v0.0.26...v1.0.0-release.1) (2024-07-05)


### Bug Fixes

* Adjust commit message formatting in auto-pr workflow ([e14e1be](https://github.com/djh00t/klingon_tools/commit/e14e1be7b18d7d4735cee07b5c8667ec0191c5c1))
* Update GitHub CLI installation in auto-pr workflow ([f5c09f6](https://github.com/djh00t/klingon_tools/commit/f5c09f671c88a0a676b7dceae3c916d2dd24271a))


* 🐛 fix(workflow):Update auto-pr workflow ([59b68cf](https://github.com/djh00t/klingon_tools/commit/59b68cf8ffcb69e30260ca0328a2277ece839cb7))
* ✨ feat(ci): enhance PR creation workflow ([fbc51ba](https://github.com/djh00t/klingon_tools/commit/fbc51ba282e23300fe4d0d2348e74b2a3e2b9340))
* ✨ feat(klingon_tools/git_validate_commit.py): add functions for validating Git ([016f389](https://github.com/djh00t/klingon_tools/commit/016f389f1abd805cd5d85d51e64db085aabfb442))


### Features

* Add auto PR workflow for new branches ([96d369f](https://github.com/djh00t/klingon_tools/commit/96d369fd220d05cf30741840f16ff099b76184a0))
* Add git_push functionality to handle pushing changes to remote ([c5e5b12](https://github.com/djh00t/klingon_tools/commit/c5e5b12958634a463d57d953fbc7f693fbdeac2d))
* Add GitHub Actions workflow for automatic pull requests creation ([a0ed313](https://github.com/djh00t/klingon_tools/commit/a0ed3131427d130ed419555ccfd3a7e153519639))
* Add GitHub CLI installation and commit messages fetching to auto-pr ([fad1e67](https://github.com/djh00t/klingon_tools/commit/fad1e6705bad0127f390495c3eeccaa7cc0de2e2))
* Add signed-off-by information to commit message if not present ([f97e034](https://github.com/djh00t/klingon_tools/commit/f97e0345df4d4ac7e70341d919a626763347857e))
* **ci:** Add workflow_dispatch event trigger in GitHub Actions workflow ([db4eb2e](https://github.com/djh00t/klingon_tools/commit/db4eb2e05a2b037e471653db5da229dd42e27d75))
* **git_tools:** Add commit message validation before pushing changes ([be5b2c4](https://github.com/djh00t/klingon_tools/commit/be5b2c4cc8806e6e2a5cbc9a9fa4db390231dc8e))
* **git_user_info:** add functionality to retrieve user's name and email from ([ec8e1e7](https://github.com/djh00t/klingon_tools/commit/ec8e1e76e25ffe7aa1a8b385f43d827eb80b1262))
* **git:** add signed-off-by information to commit messages ([a899489](https://github.com/djh00t/klingon_tools/commit/a899489b59f64730fd9fe6be1d8f62e819c6747f))
* **git:** Push new branch upstream if necessary ([e5f3d92](https://github.com/djh00t/klingon_tools/commit/e5f3d92b5bb77059a480a115c056f756a8a55de9))
* improve PR title generation and workflow automation ([#49](https://github.com/djh00t/klingon_tools/issues/49)) ([f40c445](https://github.com/djh00t/klingon_tools/commit/f40c4450fe7ef4bf0eae9bc4f2a1bddaf1f511a3))
* **klingon_tools:** Add function to retrieve git user info ([cbb52c9](https://github.com/djh00t/klingon_tools/commit/cbb52c99e3c920398b5c8b33ed329b9a4c52751e))
* **klingon_tools:** Add git_validate_commit.py to validate commit messages ([2c29bb0](https://github.com/djh00t/klingon_tools/commit/2c29bb0feb864fdf202b223cc3bc5c533dbdd659))
* **openai:** Add get_git_user_info function call and Signed-off-by footer ([dab7b1b](https://github.com/djh00t/klingon_tools/commit/dab7b1b47c2121ea8564cf221c0c3a29c920f37c))
* **push:** add global repo variable in main function ([57d815c](https://github.com/djh00t/klingon_tools/commit/57d815cf81fcb0f4f5563309b134eacc265bbc33))
* **push:** import validate_commit_messages function in git_tools.py ([1ddb015](https://github.com/djh00t/klingon_tools/commit/1ddb015c03daeab2e1251191262e7c7fb8f2d878))
* Update commit message generation in `openai_tools.py` ([0974840](https://github.com/djh00t/klingon_tools/commit/0974840a0e35e6c1ef9134f643565b4ebd317d5c))
* Update git_tools.py with commit message validation and generation logic ([c0e0b62](https://github.com/djh00t/klingon_tools/commit/c0e0b6275838b8da194057e70fc6642f251c4b78))
* Update git_validate_commit.py to include OpenAI commit message ([73b7124](https://github.com/djh00t/klingon_tools/commit/73b712494f08c7962c04fc17945a6ca7ce1d6359))
* Update pull request creation command to include mention of actor ([eb0f2f7](https://github.com/djh00t/klingon_tools/commit/eb0f2f79d5befdf333ffd2d643270bcb225d03e7))


### BREAKING CHANGES

* This commit modifies the auto-pr workflow behavior.

Signed-off-by: David Hooton <david@hooton.org>
* This commit modifies the PR creation process to ensure single
PR creation per branch.

Signed-off-by: David Hooton <david@hooton.org>
* These changes introduce new functions and enhance commit
message validation capabilities.

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0-release.1](https://github.com/djh00t/klingon_tools/compare/v0.0.26...v1.0.0-release.1) (2024-07-05)


### Bug Fixes

* Adjust commit message formatting in auto-pr workflow ([e14e1be](https://github.com/djh00t/klingon_tools/commit/e14e1be7b18d7d4735cee07b5c8667ec0191c5c1))
* Update GitHub CLI installation in auto-pr workflow ([f5c09f6](https://github.com/djh00t/klingon_tools/commit/f5c09f671c88a0a676b7dceae3c916d2dd24271a))


* 🐛 fix(workflow):Update auto-pr workflow ([59b68cf](https://github.com/djh00t/klingon_tools/commit/59b68cf8ffcb69e30260ca0328a2277ece839cb7))
* ✨ feat(ci): enhance PR creation workflow ([fbc51ba](https://github.com/djh00t/klingon_tools/commit/fbc51ba282e23300fe4d0d2348e74b2a3e2b9340))
* ✨ feat(klingon_tools/git_validate_commit.py): add functions for validating Git ([016f389](https://github.com/djh00t/klingon_tools/commit/016f389f1abd805cd5d85d51e64db085aabfb442))


### Features

* Add auto PR workflow for new branches ([96d369f](https://github.com/djh00t/klingon_tools/commit/96d369fd220d05cf30741840f16ff099b76184a0))
* Add git_push functionality to handle pushing changes to remote ([c5e5b12](https://github.com/djh00t/klingon_tools/commit/c5e5b12958634a463d57d953fbc7f693fbdeac2d))
* Add GitHub Actions workflow for automatic pull requests creation ([a0ed313](https://github.com/djh00t/klingon_tools/commit/a0ed3131427d130ed419555ccfd3a7e153519639))
* Add GitHub CLI installation and commit messages fetching to auto-pr ([fad1e67](https://github.com/djh00t/klingon_tools/commit/fad1e6705bad0127f390495c3eeccaa7cc0de2e2))
* Add signed-off-by information to commit message if not present ([f97e034](https://github.com/djh00t/klingon_tools/commit/f97e0345df4d4ac7e70341d919a626763347857e))
* **ci:** Add workflow_dispatch event trigger in GitHub Actions workflow ([db4eb2e](https://github.com/djh00t/klingon_tools/commit/db4eb2e05a2b037e471653db5da229dd42e27d75))
* **git_tools:** Add commit message validation before pushing changes ([be5b2c4](https://github.com/djh00t/klingon_tools/commit/be5b2c4cc8806e6e2a5cbc9a9fa4db390231dc8e))
* **git_user_info:** add functionality to retrieve user's name and email from ([ec8e1e7](https://github.com/djh00t/klingon_tools/commit/ec8e1e76e25ffe7aa1a8b385f43d827eb80b1262))
* **git:** add signed-off-by information to commit messages ([a899489](https://github.com/djh00t/klingon_tools/commit/a899489b59f64730fd9fe6be1d8f62e819c6747f))
* **git:** Push new branch upstream if necessary ([e5f3d92](https://github.com/djh00t/klingon_tools/commit/e5f3d92b5bb77059a480a115c056f756a8a55de9))
* improve PR title generation and workflow automation ([#49](https://github.com/djh00t/klingon_tools/issues/49)) ([f40c445](https://github.com/djh00t/klingon_tools/commit/f40c4450fe7ef4bf0eae9bc4f2a1bddaf1f511a3))
* **klingon_tools:** Add function to retrieve git user info ([cbb52c9](https://github.com/djh00t/klingon_tools/commit/cbb52c99e3c920398b5c8b33ed329b9a4c52751e))
* **klingon_tools:** Add git_validate_commit.py to validate commit messages ([2c29bb0](https://github.com/djh00t/klingon_tools/commit/2c29bb0feb864fdf202b223cc3bc5c533dbdd659))
* **openai:** Add get_git_user_info function call and Signed-off-by footer ([dab7b1b](https://github.com/djh00t/klingon_tools/commit/dab7b1b47c2121ea8564cf221c0c3a29c920f37c))
* **push:** add global repo variable in main function ([57d815c](https://github.com/djh00t/klingon_tools/commit/57d815cf81fcb0f4f5563309b134eacc265bbc33))
* **push:** import validate_commit_messages function in git_tools.py ([1ddb015](https://github.com/djh00t/klingon_tools/commit/1ddb015c03daeab2e1251191262e7c7fb8f2d878))
* Update commit message generation in `openai_tools.py` ([0974840](https://github.com/djh00t/klingon_tools/commit/0974840a0e35e6c1ef9134f643565b4ebd317d5c))
* Update git_tools.py with commit message validation and generation logic ([c0e0b62](https://github.com/djh00t/klingon_tools/commit/c0e0b6275838b8da194057e70fc6642f251c4b78))
* Update git_validate_commit.py to include OpenAI commit message ([73b7124](https://github.com/djh00t/klingon_tools/commit/73b712494f08c7962c04fc17945a6ca7ce1d6359))
* Update pull request creation command to include mention of actor ([eb0f2f7](https://github.com/djh00t/klingon_tools/commit/eb0f2f79d5befdf333ffd2d643270bcb225d03e7))


### BREAKING CHANGES

* This commit modifies the auto-pr workflow behavior.

Signed-off-by: David Hooton <david@hooton.org>
* This commit modifies the PR creation process to ensure single
PR creation per branch.

Signed-off-by: David Hooton <david@hooton.org>
* These changes introduce new functions and enhance commit
message validation capabilities.

Signed-off-by: David Hooton <david@hooton.org>
