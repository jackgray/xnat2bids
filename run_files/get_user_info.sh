#!/bin/env bash

# UID/GID setup for permissions handling
# Pull group ID from project_id (working_gid)
groupinfo=$(getent group ${project_id})
while IFS=$':' read -r -a tmp ; do
working_gid="${tmp[2]}"
userinfo="${tmp[3]}"
done <<< $groupinfo
username=$(whoami)
working_uid="$(id -u ${username})"
echo primary gid for ${project_id}: $working_gid
echo your uid: $working_uid