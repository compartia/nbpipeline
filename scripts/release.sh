
export PATH="~/.local/bin/:$PATH"


# Get the current project version from poetry
version=$(poetry version -s)

echo  $version

# Add a new git tag with the version
git tag "v$version"

# Push the tag to the remote repository
git push origin "v$version"
