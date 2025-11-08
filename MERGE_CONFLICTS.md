# Handling Merge Conflicts in Jupyter Notebooks

## Problem
When merging branches with Jupyter notebooks, Git sometimes inserts conflict markers like:
```
<<<<<<< HEAD
[content from current branch]
=======
[content from other branch]
>>>>>>> main
```

These markers break the JSON structure of `.ipynb` files, making them unreadable in Jupyter/DataSpell.

## Solution: nbdime

We've installed **nbdime** (Notebook Diff and Merge), a tool specifically designed for Jupyter notebooks.

### Already Configured

✅ `nbdime` is installed (see `requirements.txt`)
✅ Git is configured to use nbdime for notebook merging
✅ `.gitattributes` tells Git to use nbdime for `.ipynb` files

### When a Merge Conflict Occurs

#### Option 1: Use nbdime GUI (Recommended)

If you get a merge conflict in a notebook:

```bash
# Start the interactive merge tool
git mergetool --tool=nbdime

# This opens a web-based interface showing:
# - Base version (common ancestor)
# - Local version (your changes)
# - Remote version (incoming changes)
# - Merged result
```

The GUI lets you:
- See changes side-by-side
- Choose which changes to keep
- Merge intelligently (code vs outputs vs metadata)
- Save the resolved version

#### Option 2: Manual Resolution

If you see conflict markers in a notebook:

1. **Check for markers:**
   ```bash
   grep -n "<<<<<<\|======\|>>>>>>" notebooks/*.ipynb
   ```

2. **Open the file** in a text editor (NOT DataSpell/Jupyter)

3. **Find and remove** the conflict markers:
   - `<<<<<<< HEAD`
   - `=======`
   - `>>>>>>> branch-name`

4. **Keep the correct content** between the markers

5. **Validate the JSON:**
   ```bash
   python -m json.tool notebooks/03_comparative_analysis.ipynb > /dev/null
   ```

   If valid, you'll see no output. If invalid, fix the JSON structure.

6. **Mark as resolved:**
   ```bash
   git add notebooks/03_comparative_analysis.ipynb
   git commit -m "Resolve merge conflict in notebook"
   ```

#### Option 3: Choose One Side

If you just want to use one version completely:

```bash
# Use the current branch version (ours)
git checkout --ours notebooks/03_comparative_analysis.ipynb

# OR use the incoming branch version (theirs)
git checkout --theirs notebooks/03_comparative_analysis.ipynb

# Then mark as resolved
git add notebooks/03_comparative_analysis.ipynb
```

### Preventing Conflicts

1. **Clear outputs before committing:**
   ```bash
   # In Jupyter: Cell -> All Output -> Clear
   ```

   This reduces conflicts since output data changes frequently.

2. **Work on different notebooks** in different branches when possible

3. **Pull frequently** to stay up-to-date with the main branch

### Fixing a Corrupted Notebook

If a notebook is already corrupted with conflict markers:

```bash
# Validate it's corrupted
python -m json.tool notebooks/03_comparative_analysis.ipynb

# Option 1: Restore from a previous commit
git checkout HEAD~1 -- notebooks/03_comparative_analysis.ipynb

# Option 2: Restore from a specific commit
git log --oneline -- notebooks/03_comparative_analysis.ipynb
git checkout <commit-hash> -- notebooks/03_comparative_analysis.ipynb

# Option 3: Use nbdime to merge
git show HEAD:notebooks/03_comparative_analysis.ipynb > /tmp/head_version.ipynb
git show main:notebooks/03_comparative_analysis.ipynb > /tmp/main_version.ipynb
nbdime merge /tmp/main_version.ipynb /tmp/head_version.ipynb /tmp/base_version.ipynb -o notebooks/03_comparative_analysis.ipynb
```

### Quick Reference

| Problem | Command |
|---------|---------|
| Check for conflict markers | `grep "<<<<<<" notebooks/*.ipynb` |
| Validate JSON | `python -m json.tool notebook.ipynb > /dev/null` |
| Launch merge tool | `git mergetool --tool=nbdime` |
| Use current version | `git checkout --ours notebook.ipynb` |
| Use incoming version | `git checkout --theirs notebook.ipynb` |
| Restore from commit | `git checkout <commit> -- notebook.ipynb` |

### Need Help?

If you're still stuck:
1. Check which files have conflicts: `git status`
2. See the conflict markers: `cat notebooks/notebook.ipynb | grep -A 5 -B 5 "<<<<<<"`
3. Use nbdime GUI for visual resolution: `git mergetool --tool=nbdime`

## Resources

- [nbdime Documentation](https://nbdime.readthedocs.io/)
- [Git Merge Strategies](https://git-scm.com/docs/merge-strategies)
