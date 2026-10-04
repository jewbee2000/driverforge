# Evidence directory

Current application evidence is recorded here. No live-model or physical runs occurred.

- requirements-evidence.json and checks/: executed requirement mapping, commands,
  exit codes, environment/oracle/input/log hashes.
- baseline.json, code-size.json, upstream.json: existing-tool comparison, code/config
  size and unchanged public-driver source identity.
- consumer/: wheel installation, non-default input, failure and configuration repair.
- fresh-install.json: clean source checkout/install and check commands.
- performance.json: three fresh worker measurements per workload and frozen limits.
- licenses.json: 42 pinned distribution license declarations and notice paths.
- signed-failure.png: actual report screenshot used in the unpublished blog.

Progress history and prior failures remain available; current results do not erase them.

Each manifest must identify run mode (deterministic, replay, live), source commit, dirty diff hash if any, requirement IDs, input and oracle hashes, environment versions, commands, exit codes, artifacts, and limitations. Live runs additionally record actual model/provider, attempts, tokens when available, time, budget, and costs when known. Preserve unavailable values as null; never replace them with invented zeros.
