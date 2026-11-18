# Difference Atlas

Open [the research map](dist/index.html) in a browser. The checked-in snapshot
works offline, including the proof readers, source code, and result downloads.
Links to published papers open their external sources.

To monitor the working repository, run the local server from the repository root.

```sh
uv run research-atlas/serve.py
```

Open http://127.0.0.1:8764 and refresh after changing a proof, program, dataset,
or topic. The server rebuilds changed evidence on request. Use `--port` to
choose another port. The first build uses uv to install the pinned Pandoc
package. To rebuild the portable site once, run the following command.

```sh
uv run research-atlas/build.py
```

## Updating the map

Edit `topics.json` to add a research question, record a proof, or change its
attribution. Each topic has a stable ID, a branch, a status, and an attribution
note with source references. Use the source registry for papers and the
repository-relative paths for proof, code, figure, or data links. The build
checks IDs and references, reads experiment summaries, and generates portable
pages with locally typeset mathematics. To introduce a new evidence file, add
it to the corresponding source list in `build.py`.

The **Progress** view groups the same topics by completion status or by
attribution. **Project derivation** records a result derived in the notebook
whose publication priority is unverified. **Project experiment** identifies a
measurement produced here. **Published** and **Corollary** link to the source
and explain its role. **Open question** describes work still open in the
project. Update the literature review date in the catalog when references have
actually been reviewed.

The local server reads the working tree. A hosted or copied snapshot changes
when the updated `dist/` is published or copied again.
