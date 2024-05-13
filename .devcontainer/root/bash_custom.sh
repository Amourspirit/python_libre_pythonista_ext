# if using vs code insiders then create an alias as code for convienience
if ! which code >/dev/null && which code-insiders >/dev/null; then
    alias code=$(which code-insiders)
fi