## [2.3.0-release.3](https://github.com/djh00t/klingon_tools/compare/v2.3.0-release.2...v2.3.0-release.3) (2024-07-22)


### Bug Fixes

* **workflow:** update source branch retrieval in release workflow ([0462193](https://github.com/djh00t/klingon_tools/commit/0462193422597c1046757d4eddfff382e7d5ffbd))

## [2.3.0-release.2](https://github.com/djh00t/klingon_tools/compare/v2.3.0-release.1...v2.3.0-release.2) (2024-07-22)


### Bug Fixes

* **workflows/release.yaml:** correct source branch assignment in PR creation ([b516435](https://github.com/djh00t/klingon_tools/commit/b516435687d305e2e861a598f1dce6b084372a76))

## [2.3.0-release.1](https://github.com/djh00t/klingon_tools/compare/v2.2.1-release.1...v2.3.0-release.1) (2024-07-22)


### Features

* **github/workflows/release:** rename create-pr to create-release-pr and ([bd938e5](https://github.com/djh00t/klingon_tools/commit/bd938e5a7bca2df47941257397c88590f4eed65a))

## [2.2.1-release.1](https://github.com/djh00t/klingon_tools/compare/v2.2.0...v2.2.1-release.1) (2024-07-22)

## [2.2.0](https://github.com/djh00t/klingon_tools/compare/v2.1.0...v2.2.0) (2024-07-22)


### Features

* **update_version.py:** add script to update version in package.json and ([362bf44](https://github.com/djh00t/klingon_tools/commit/362bf44a4dd2070b2257d86f5935b473657b126c))
* **github/workflows/semantic-release.sh:** add version update logging for ([86b73ea](https://github.com/djh00t/klingon_tools/commit/86b73ea77e090921925d886e670cad900471d1d5))


### Bug Fixes

* **package.json:** bump version to 2.1.1 ([902f867](https://github.com/djh00t/klingon_tools/commit/902f86760a603c4f19a4eafd6fd8620910882d21))
* **workflows/semantic-release.sh:** correct paths to package.json and ([4cdbfed](https://github.com/djh00t/klingon_tools/commit/4cdbfeded8f22909bbfc0c12c5f96fbda85d480e))
* **semantic-release.sh:** correct version extraction and replacement syntax in ([7ca0c5d](https://github.com/djh00t/klingon_tools/commit/7ca0c5d05a83d9d4a73524369b05da21d0895512))
* **semantic-release:** correct version extraction from package.json ([2f1c011](https://github.com/djh00t/klingon_tools/commit/2f1c01183c7ed844fa22ddf4ddb70a971907113b))
* **semantics:** improve semantic-release workflow for version updates ([df49f3e](https://github.com/djh00t/klingon_tools/commit/df49f3e66df0d8cba5d931dba677c324640580ed))
* **.releaserc.js:** remove exec command for version update in release process ([390b54b](https://github.com/djh00t/klingon_tools/commit/390b54bf749f806e1cb8ef884a6eea7f521726b4))
* **openai_tools:** simplify generate_pull_request_body method ([6c16e36](https://github.com/djh00t/klingon_tools/commit/6c16e3650fdb5b971baded5b2fad953cfcb01bd7))
* **.releaserc.js:** update prepareCmd to include an empty argument for sed on ([f9f2477](https://github.com/djh00t/klingon_tools/commit/f9f24770a852725469917c97eb8defa3c580c105))
* **.releaserc.js:** update prepareCmd to include pwd command for better ([4285516](https://github.com/djh00t/klingon_tools/commit/42855161b59a8154ad988aa32ca09a1e39b6fb64))
* **semantic-release:** update version in pyproject.toml during release process ([e49674e](https://github.com/djh00t/klingon_tools/commit/e49674ea927dcda9bffb9203f085fc647b8c009f))
* **pyproject.toml:** update version to use nextRelease.version variable ([07a4563](https://github.com/djh00t/klingon_tools/commit/07a45637c9e1a08398d37b19441b101547bb1609))

## [2.1.0](https://github.com/djh00t/klingon_tools/compare/v2.0.1...v2.1.0) (2024-07-20)


### Features

* **openai_tools:** add dry run functionality to unstage files ([8316f86](https://github.com/djh00t/klingon_tools/commit/8316f86aa76bd33c4a76f4c9dee4cfc6335d0e26))
* **entrypoints:** add dryrun parameter to pull request summary and context ([976c6a6](https://github.com/djh00t/klingon_tools/commit/976c6a6be6056a316e337a15a7ed11d9e458c1ae))
* **git_tools:** add function to unstage files from the repository ([9b467d0](https://github.com/djh00t/klingon_tools/commit/9b467d0c99706252c0fae4f53f26a9e1f3f24b3e))
* **tests/test_openai_tools:** add unit tests for OpenAITools functionality ([a9749af](https://github.com/djh00t/klingon_tools/commit/a9749af54882622e07a57d95c90482a3a497275a))


### Bug Fixes

* **github-actions:** Configure Git for GitHub CLI in auto-pr workflow ([d8da557](https://github.com/djh00t/klingon_tools/commit/d8da55780e70cf8dc000c2f1200dbace5e96a07e))
* **.github/workflows/release:** configure Git settings for GitHub CLI ([ff38752](https://github.com/djh00t/klingon_tools/commit/ff387523276440f03f1062ce0e00fdcaac88b2c4))
* **push.py:** correct argument order in git_commit_deletes function call ([2c9ba21](https://github.com/djh00t/klingon_tools/commit/2c9ba211806d37f87998af6d32049e231bd40528))
* **setup.py:** correct file opening mode in get_version function ([0d7f010](https://github.com/djh00t/klingon_tools/commit/0d7f01040ad9b7c1616a3a59ee787f8cc698b0a1))
* **pr_body_gen.py:** handle errors during summary generation ([a89f171](https://github.com/djh00t/klingon_tools/commit/a89f17158df6f1dff923aff06546b2b28fd40a5d))
* **openai_tools:** handle errors when generating pull request summary and ([8a2814c](https://github.com/djh00t/klingon_tools/commit/8a2814c9f06da41a296b08df4580b7a9afcc3408))
* **pr_body_gen:** handle subprocess errors in context generation ([10977ed](https://github.com/djh00t/klingon_tools/commit/10977edd018bc45c62e3afc9d6c363a28fbe004d))
* **.releaserc.js:** update headerPattern for better commit message parsing ([4fa2bee](https://github.com/djh00t/klingon_tools/commit/4fa2beec5ce0fe05fa247c80ca95af754a81b92a))
* **.releaserc.js:** update headerPattern to support emoji characters ([4913ce4](https://github.com/djh00t/klingon_tools/commit/4913ce44ff54171a6a057ce830b2946e3156ab14))
* **setup.py:** update version retrieval logic in setup.py ([cbadfc3](https://github.com/djh00t/klingon_tools/commit/cbadfc316807c9a246d3e603f527c20b69c08fe0))

## [2.0.1](https://github.com/djh00t/klingon_tools/compare/v2.0.0...v2.0.1) (2024-07-19)

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
