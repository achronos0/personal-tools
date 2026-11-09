# Helpful MacOS zsh configuration
# v2.3.3 2023-08-22

##############################
#
# This script configures your shell to add many conveniences.
# If you are not familiar with Unix-like shell environments, this is an easy off-the-shelf helper.
#
# ==Installation==
#
# 1. Create a subdirectory named "bin" inside your home directory: ~/bin
#    You can use Finder or Terminal.
#    From Terminal:
#        mkdir ~/bin
# 2. Move this file into that new directory
#    You can use Finder or Terminal.
#    From Terminal, if this file is in Downloads:
#        mv ~/Downloads/macos_shell_helper.sh ~/bin
# 3. Edit your shell configuration file: ~/.zshrc
#    Create the file if it doesn't already exist:
#        touch ~/.zshrc
#    Open the file in your default text editor application:
#        open ~/bin/macos_shell_helper.sh
# 4. Add this script to the config file
#    Insert this line at the top:
#        source ~/bin/macos_shell_helper.sh
#    Optionally, provide settings to control what this script does:
#        export HELPER_OPTIONS="color=0 nvm_autoload='foo bar'"
#        source ~/bin/macos_shell_helper.sh
#    See next section for a list of options.
#
# ==Options==
#
# color=1
#    Show colourful text.
#    1 to enable, 0 to disable.
#    Default: 1
# prompt=1
#    Show command prompt as nicely formatted current directory (1=enable, 0=disable).
#    1 to enable, 0 to disable.
#    Default: 1
# list_on_cd=1
#    Automtically show directory list and git info after changing to directory (`cd`)
#    1 to enable, 0 to disable.
#    Default: 1
# cli_editor=nano
#    Text editor to use inside shell.
#    Common editor choices are `nano` and `vi`.
#    Default: nano
# nvm_autoload=0
#    Load node version manager (nvm) on demand when nvm or npm or node is called.
#    1 to enable, 0 to disable.
#    Can also set a list of additional commands on which to autoload, e.g. `nvm_autoload=pnpm,my-node-command`.
#    Default: 0
# path=1
#    Ensure executable PATH includes everything it should have.
#    1 to enable, 0 to disable.
#    Default: 1
# shell=1
#    Set shell configuration settings to nice values.
#    1 to enable, 0 to disable.
#    Default: 1
# friendly_commands=1
#    Set friendly defaults for basic commands like `cp` and `mv`.
#    1 to enable, 0 to disable.
#    Default: 1
# helper_commands=1
#    Add many helpful commands for working in shell on MacOS.
#    See next section for a list of commands.
#    1 to enable, 0 to disable.
#    Default: 1
#
# ==Helper commands==
#
# Change directory
#    cd1, cd2, ..., cd8
#        Change current directory to `n`th ancestor (`cd ../../etc`)
#
# List files:
#    ll [dir...]
#        List directory in long form (`ls -l`).
#    l
#        Because sometimes even ll is too long.
#    lt [dir...]
#        List directory tree recursively as a hierarchy (requires `eza` to be installed).
#    f <text>
#        Find files containing text, in current directory and recursively in subdirectories.
#    r <regexp>
#        Find files matching regular expression (PCRE) pattern, in current directory and recursively in subdirectories.
#    findname <filename>
#        Find files by name, in current directory and recursively in subdirectories.
#        Name can contain wildcards if quoted, e.g. `findname '*.jpg'`.
#    path
#        Show list of directories where shell looks for commands to run.
#
# MacOS general:
#    look <file>
#        Open file in MacOS Quicklook Preview.
#    spotlight <search-text>
#        Search for a file using MacOS Spotlight's metadata.
#    trash <path>
#        Move file to the MacOS Trash.
#    rmds
#        Delete .DS_Store files in current directory and recursively in subdirectories.
#
# Terminal:
#    cdt <dir>
#        Change to directory in a new Terminal tab.
#    fix_stty
#        Restore messed up terminal settings.
#    set_terminal_title <title>
#        Set the Terminal tab titlebar text.
#
# Finder:
#   pfd
#       Show Finder's current directory ("print finder directory").
#
# Git:
#    ga [files]
#        Add files to staging, or all changed files if none provided.
#        Like `git add` or `git add --all`.
#    gb [pattern]
#        List branches.
#        With pattern, list only matching branches.
#        Like `git branch --all`.
#    gbl
#        List local branches.
#        Like `git branch`.
#    gc '<message>'
#        Commit and push staged changes.
#        Like `git commit -m '<message>' && git push`.
#    gca '<message>'
#        Commit and push all new and changed files
#        Like `git add --all && git commit -m '<message>' && git push`.
#    gcr
#        Redo and push current commit, adding staged changes.
#        Like `git commit --amend && git push --force`.
#    gcra
#        Redo and push current commit, adding all new and changed files.
#        Like `git add --all && git commit --amend && git push --force`.
#    gd [files]
#        Show diff of working dir files.
#        Like `git diff`
#    gi
#        Show working directory information: fetch updates, then show a short summary of current state.
#        Like `git fetch && git show && git status`
#    gg <branch>
#        Go to branch. If branch doesn't exist, create it and create remote branch.
#        Like `git switch <branch>` or `git switch --create <branch>`.
#    ggp <branch>
#        Go to branch and pull changes.
#        Like `git switch <branch> && git pull`
#    gl
#        Show commit history.
#        Like `git log`.
#    gld [start-date] [end-date]
#        Show commit history for a date range.
#        Like `git log --after=<start-date> --before=[end-date]`.
#        With no arguments, shows commits from today.
#    gp
#        Run pull and push.
#        Like `git pull && git push`.
#    gpf
#        Force push.
#        Like `git push --force`.
#    gs
#        Show current working directory status.
#        Like `git status`.
#    gx [branch]
#        Delete branch from local and remote.
#        If branch is not provided, current branch is deleted.
#        Like `git branch --delete --force foo && git push --delete origin foo`.
#    lg [dir]
#        List git repositories recursively; for each, run git fetch then show git status summary (`gi`).
#    lgld <start-date> <end-date> [dir]
#        Find git repositories recursively, show combined commit history for a date range (`gld`).
#    mg <dir> <command> [args...]
#        Find git repositories recursively, run a command on each one.
#
# GitHub:
#    ghpr <target-branch>
#        Create GitHub pull request (PR) to merge from the current branch to the specified target branch.
#        Like `gh pr create --fill --base=<merge-to-branch>`
#
# Visual Studio Code:
#    code [dir...]
#        Open files/directories in existing VS Code window/workspace
#    code <file>...
#        Open files/directories in existing VS Code window/workspace
#    codediff <left-file> <right-file>
#        Open diff (file differences view) in VS Code
#
# Node utils:
#    ne <javascript-expression...>
#        Execute javascript expression(s) using node, output result
#
##############################

macos_shell_helper () {
	# Parse configuration options
	local DEFAULT_OPTIONS="color=1 prompt=1 list_on_cd=1 cli_editor=nano nvm_autoload=0 path=1 shell=1 friendly_commands=1 helper_commands=1"
	local VAL=
	for VAL in ${=DEFAULT_OPTIONS} ${=HELPER_OPTIONS}
	do
		local OPTKEY=$(echo "$VAL" | sed 's/=.*//' | tr a-z A-Z)
		local OPTVAL=$(echo "$VAL" | sed 's/[^=]*=//')
		local OPT_$OPTKEY="$OPTVAL"
	done
	unset HELPER_OPTIONS

	# Show colour output
	if [[ "$OPT_COLOR" == "1" ]] ; then
		export CLICOLOR=1
		export LSCOLORS=ExFxBxDxCxegedabagacad
	fi

	# Set prompt
	if [[ "$OPT_PROMPT" == "1" && `whoami` != "root" ]] ; then
		conditional_prompt() {
			local CWD=$(dirs)
			local LEN=${#CWD};
			if [[ $LEN -gt 60 ]] ; then
				export PROMPT='%~'$'\n''%# '
			else
				export PROMPT='%~ %# '
			fi
		}
		precmd_functions+=(conditional_prompt)
		export precmd_functions
	fi

	# Show directory list on cd
	if [[ "$OPT_LIST_ON_CD" == "1" ]] ; then
		if [[ "$OPT_HELPER_COMMANDS" == "1" ]] ; then
			cd() {
				builtin cd "$@";
				if [[ $? -eq 0 ]] ; then
					$(whence ll)
					if [[ -d .git ]] ; then
						gi nofetch
					fi
				fi
			}
		else
			cd() { builtin cd "$@"; if [[ $? -eq 0 ]] ; then ls -l; fi; }
		fi
	fi

	# Set command-line editor
	if [[ ! -z "$OPT_CLI_EDITOR" ]] ; then
		export EDITOR=$(whence "$OPT_CLI_EDITOR")
	fi

	# Load nvm on demand
	if [[ "$OPT_NVM_AUTOLOAD" != "0" && -f "$HOME/.nvm/nvm.sh" && -z "$NVM_DIR" ]] ; then
		local NVM_COMMANDS="nvm npm node"
		if [[ "$OPT_NVM_AUTOLOAD" != "1" ]] ; then
			NVM_COMMANDS+=(${OPT_NVM_AUTOLOAD//,/' '})
		fi
		eval "$(<<-EOF
			loadnvm () {
				echo "Loading nvm"
				unset -f loadnvm $NVM_COMMANDS
				export NVM_DIR="$HOME/.nvm"
				[ -s "\$NVM_DIR/nvm.sh" ] && \. "\$NVM_DIR/nvm.sh" # This loads nvm
			}
		EOF
		)"
		local VAL=
		for VAL in ${=NVM_COMMANDS}
		do
			eval "$VAL () { loadnvm && $VAL \"\$@\" ; }"
		done
	fi

	# Add missing directories to path
	if [[ "$OPT_PATH" == "1" ]] ; then
		local DIRS="/usr/local/sbin /usr/local/bin /usr/local /Users/$USER/bin"
		for VAL in ${=DIRS} ; do
			if [[ ! -d "$VAL" ]] ; then
				continue
			fi
			case ":$PATH:" in
				*":$VAL:"*)
					:
					;;
				*)
					PATH+=":$VAL"
					;;
			esac
		done
	fi

	# Configure shell
	if [[ "$OPT_SHELL" == "1" ]] ; then
		# Make input editor treat "/" and others as separate words when moving cursor
		export WORDCHARS='*?_-.[]~!#$%^{}<>'
	fi

	# Configure basic commands
	if [[ "$OPT_FRIENDLY_COMMANDS" == "1" ]] ; then
		# Set common env vars used by many commands
		export BLOCKSIZE=1k

		# Replace standard commands with friendly defaults
		alias cp='cp -iv'
		alias mv='mv -iv'
		alias mkdir='mkdir -pv'
		alias less='less -FSRXc'
		if [[ -x /usr/local/bin/ggrep ]] ; then
			# If gnu coreutils is installed use its grep
			alias grep="GREP_COLORS='mc=01;31:fn=35' ggrep --color=auto --perl-regexp"
			alias fgrep="GREP_COLORS='mc=01;31:fn=35' ggrep --color=auto --fixed-strings --ignore-case"
		fi
	fi

	# Define helper commands
	if [[ "$OPT_HELPER_COMMANDS" == "1" ]] ; then
		# Change directory
		alias cd1="cd .."
		alias cd2="cd ../.."
		alias cd3="cd ../../.."
		alias cd4="cd ../../../.."
		alias cd5="cd ../../../../.."
		alias cd6="cd ../../../../../.."
		alias cd7="cd ../../../../../../.."
		alias cd8="cd ../../../../../../../.."

		# List files
		if [[ $(whence gls) ]] ; then
			# If gnu coreutils is installed use its ls
			alias ll='gls -l --almost-all --dereference-command-line-symlink-to-dir --color=auto --file-type --group-directories-first --human-readable --no-group --quoting-style=literal'
		else
			alias ll='ls -FGlAhp'
		fi
		alias l='ll'
		if [[ $(whence eza) ]] ; then
			alias lt='eza --long --group-directories-first --sort=Name --tree'
		fi
		alias f="fgrep --recursive --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=build --exclude-dir=dist --exclude=package-lock.json"
		alias r="grep --recursive --exclude-dir=node_modules --exclude-dir=.git"
		alias findname="find . -name "
		alias path='echo -e ${PATH//:/\\n}'

		# MacOS general
		look () {
			qlmanage -p "$*" >& /dev/null
		}
		spotlight () {
			mdfind "kMDItemDisplayName == '$@'wc"
		}
		trash () {
			command mv "$@" ~/.Trash
		}
		alias rmds="find . -type f -name '*.DS_Store' -ls -delete"

		# Terminal
		cdt () {
			open -a Terminal "$@"
		}
		fix_stty () {
			stty sane
		}
		set_terminal_title () {
			local TITLE="$1"
			echo -n -e "\033]0;$TITLE\007"
		}

		# Finder
		pfd () {
			echo $( /usr/bin/osascript <<-'EOF'
				tell application "Finder"
					try
				set currFolder to (folder of the front window as alias)
					on error
				set currFolder to (path to desktop folder as alias)
					end try
					POSIX path of currFolder
				end tell
			EOF
			)
		}

		# Git
		ga () {
			if [[ -z "$1" ]] ; then
				git add --all
			else
				git add "$@"
			fi
		}
		gb () {
			if [[ -z "$1" ]] ; then
				git branch --all
			else
				git branch --all | grep "$1"
			fi
		}
		gbl () {
			git branch
		}
		gc () {
			[[ -z "$1" ]] && (echo "Error: Missing commit message" >&2) && return 1
			git pull && git commit -m "$1" && git push
		}
		gca () {
			[[ -z "$1" ]] && (echo "Error: Missing commit message" >&2) && return 1
			git pull && git add --all && git commit -m "$1" && git push
		}
		gcr () {
			git commit --amend --no-edit && git push --force-with-lease --force-if-includes
		}
		gcra () {
			git add --all && git commit --amend --no-edit && git push --force-with-lease --force-if-includes
		}
		gd () {
			git diff -w -- "$@"
		}
		gf () {
			git fetch --all --prune
		}
		gg () {
			local BRANCH=$1
			if [[ -z "$BRANCH" ]] ; then
				echo "Error: Missing branch name" >&2
				return 1
			fi
			local LOCAL=$(git branch --no-color --list "$BRANCH")
			if [[ ! -z "$LOCAL" ]] ; then
				git switch "$BRANCH"
				return
			fi
			local REMOTE=$(git branch --no-color --list --remotes "origin/$BRANCH")
			if [[ ! -z "$REMOTE" ]] ; then
				git switch "$BRANCH"
				return
			fi
			git branch "$BRANCH" && git switch "$BRANCH" && git push --set-upstream origin "$BRANCH"
		}
		ggp () {
			git switch $1 && git pull && git push && git fetch --all --prune
		}
		gi () {
			local GIT_FORMAT='%C(auto)%h%d %s %C(blue)%al%C(auto) %ci'
			if [[ "$1" != "nofetch" ]] ; then
				git fetch
				if [[ $? != 0 ]] ; then return ; fi
			fi
			git show --abbrev-commit --summary --no-patch --format="tformat:$GIT_FORMAT"
			if [[ $? != 0 ]] ; then return ; fi
			git status --short --branch --untracked-files=all
		}
		gl () {
			git log "$@"
		}
		gld () {
			local GIT_FORMAT='%C(auto) %ci %h %C(blue)%al%C(auto) %s%d'
			local START_DATE=$1
			local END_DATE=$2
			local ARGS=${*:3}
			[[ -z "$START_DATE" ]] && START_DATE=$(date '+%F')
			[[ -z "$END_DATE" ]] && END_DATE=$(date '+%F')
			START_DATE=$(date -j -v '-1d' -f '%F' $START_DATE '+%F')
			END_DATE=$(date -j -v '+1d' -f '%F' $END_DATE '+%F')
			PAGER='' git log --after=$START_DATE --before=$END_DATE --date-order --pretty="tformat:$GIT_FORMAT" $ARGS
		}
		gp () {
			git pull && git push && git fetch --all --prune
		}
		gpf () {
			git push --force-with-lease --force-if-includes
		}
		gs () {
			git status --untracked-files=all
		}
		gx () {
			local BRANCH=$1
			local CURRENT=$(git branch --show-current)
			if [[ -z "$BRANCH" ]] ; then
				BRANCH=$CURRENT
			fi
			if [[ "$BRANCH" == "main" ]] ; then
				echo "Error: Cannot delete main branch" >&2
				return 1
			fi
			if [[ "$CURRENT" == "$BRANCH" ]] ; then
				git switch main || return 1
			fi
			git pull || return 1
			git push || return 1
			git fetch --all --prune || return 1
			if [[ $(git branch --all|grep -e '^ *'"$BRANCH"'$') ]] ; then
				echo "deleting local branch: $BRANCH"
				git branch --delete --force "$BRANCH"
			fi
			if [[ $(git branch --all|grep -e '^ *remotes/origin/'"$BRANCH"'$') ]] ; then
				echo "deleting remote branch: $BRANCH"
				git push --delete origin "$BRANCH"
			fi
		}
		lg () {
			local ARG_DIRS=$*
			[[ -z "$ARG_DIRS" ]] && ARG_DIRS=.
			local GIT_DIRS=$(_ls_git $ARG_DIRS)
			_run_each_dir "$GIT_DIRS" 'echo ; _echo_grey $DIR ; gi'
		}
		lgld () {
			local START_DATE=$1
			local END_DATE=$2
			local ARG_DIRS=${*:3}
			[[ -z "$START_DATE" ]] && START_DATE=$(date '+%F')
			[[ -z "$END_DATE" ]] && END_DATE=$(date '+%F')
			[[ -z "$ARG_DIRS" ]] && ARG_DIRS=.
			local GIT_DIRS=$(_ls_git $ARG_DIRS)
			_run_each_dir "$GIT_DIRS" "gld $START_DATE $END_DATE --color | xargs -L 1 -J % echo % \$(tput setaf 8)\"[\$DIR]\"\$(tput sgr 0)" | sort --reverse
		}
		mg () {
			local DIR=$1
			local CMD=${@:2}
			if [[ -z "$DIR" ]] ; then
				echo $'Error: Missing directory.\nPass '.' to use current directory' >&2
				return 1
			fi
			if [[ -z "$CMD" ]] ; then
				echo "Error: Missing command name" >&2
				return 1
			fi
			local GIT_DIRS=$(_ls_git $DIR)
			_run_each_dir "$GIT_DIRS" "$CMD"
		}

		# GitHub
		ghpr () {
			BASE_BRANCH=$1
			if [[ -z "$BASE_BRANCH" ]] ; then
				echo "Missing target branch name\n\nCreate a GitHub PR based on the current branch\nUsage: ghpr <target-branch>\n"
				return 1
			fi
			gh pr create --fill --base=$BASE_BRANCH
		}

		# Visual Studio Code
		if [[ -x /usr/local/bin/code ]] ; then
			code() {
				if [[ -z "$1" ]] ; then
					/usr/local/bin/code --add .
					return 0
				fi
				if [[ -d "$1" ]] ; then
					local OPTS="--add"
				else
					local OPTS="--reuse-window"
				fi
				/usr/local/bin/code $OPTS $*
			}
			codediff () {
				code --diff $*
			}
		fi

		# Node utils
		ne () {
			node -e 'console.log('"$*"')'
		}

		# Internal functions
		_run_each_dir () {
			local DIRS=(${(@f)1})
			local CMD=(${(z)2})
			for DIR in $DIRS
			do
				builtin cd "$DIR"
				eval $CMD
				builtin cd - >/dev/null
			done
		}
		_ls_git () {
			local GIT_DIRS=()
			for DIR in $*
			do
				GIT_DIRS=$GIT_DIRS$'\n'$(find $DIR -type d -name node_modules -prune -o -type d -name .git -print -prune)
			done
			echo "$GIT_DIRS" | xargs -n 1 dirname | sort --unique
		}
		_echo_grey () {
			[[ -t 1 ]] && tput setaf 8
			echo $*
			[[ -t 1 ]] && tput sgr 0
		}
	fi

}
macos_shell_helper
unset -f macos_shell_helper
