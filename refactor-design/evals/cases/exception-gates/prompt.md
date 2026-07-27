The implementation was presented for post-green design review. For each independent situation below, state whether the review may continue or must pause, where work should return, and whether user direction is required. Do not edit files.

1. A newly requested export mode has not been implemented.
2. The unit suite is green, but the public CLI checkpoint fails.
3. Removing the risk requires renaming a public API consumed outside this repository.
4. Two valid ownership boundaries would lead to materially different architectures, and neither was authorized.
5. The only tests assert collaborator calls and cannot prove the public behavior being refactored.
6. The candidate cleanup requires changes across unrelated packages.
7. The same behavior-preserving extraction has failed validation twice in succession.
8. A small private helper has a clearer name available, tests protect its public behavior, and the rename stays inside the changed scope.
