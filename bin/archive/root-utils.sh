
goroot () {
	read -rsp $'Run JAMF "Make Me Admin" first. Press any key to continue...\n' -n1 key
	sudo su
}

# Make myself a sudoer:
# echo 'kpatterson ALL = (ALL) ALL' > /etc/sudoers.d/exper

# Make myself a macos admin:
# (running jamf 'Make me an admin' will undo this)
# sudo dscl . -append /groups/admin GroupMembership username

# List macos admin users:
# dscacheutil -q group -a name admin
