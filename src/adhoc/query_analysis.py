
import re
import glob
from collections import defaultdict


def normalize_query(query):
    # Replace numbers and quoted strings with placeholders
    query = re.sub(r"=\s*\d+", "= ?", query)
    query = re.sub(r"=\s*'[^']*'", "= ?", query)
    query = re.sub(r"=\s*\"[^\"]*\"", "= ?", query)
    query = re.sub(r"\d+", "?", query)
    query = re.sub(r"\s+", " ", query)
    return query.strip().lower()


from datetime import datetime

query_stats = defaultdict(lambda: {"count": 0, "total_time": 0.0, "max_time": 0.0, "rows_examined": 0, "timestamps": []})

# Change this glob pattern to match your log files
for filename in glob.glob("slow*.log"):
    with open(filename, "r") as f:
        lines = f.readlines()

    current_query = None
    current_time = 0.0
    current_rows_examined = 0
    current_timestamp = None

    for line in lines:
        if line.startswith("# Time: "):
            # Example: # Time: 250831  9:10:01
            match = re.search(r"# Time: (\d{6})\s+(\d{1,2}:\d{2}:\d{2})", line)
            if match:
                date_str = match.group(1)  # YYMMDD
                time_str = match.group(2)  # HH:MM:SS
                # Convert to yyyy-MM-dd hh:mm:ss:SSS
                year = int(date_str[:2])
                month = int(date_str[2:4])
                day = int(date_str[4:6])
                # Assume 2000+ for year
                year += 2000
                dt_str = f"{year:04d}-{month:02d}-{day:02d} {time_str}:000"
                current_timestamp = dt_str
        elif line.startswith("# Query_time:"):
            match = re.search(r"# Query_time: ([\d\.]+).*Rows_examined: (\d+)", line)
            if match:
                current_time = float(match.group(1))
                current_rows_examined = int(match.group(2))
        elif line.strip().lower().startswith("select"):
            current_query = normalize_query(line.strip())
            stats = query_stats[current_query]
            stats["count"] += 1
            stats["total_time"] += current_time
            stats["max_time"] = max(stats["max_time"], current_time)
            stats["rows_examined"] += current_rows_examined
            if current_timestamp:
                stats["timestamps"].append(current_timestamp)

# Print summary
for query, stats in sorted(query_stats.items(), key=lambda x: -x[1]["count"]):
    print(f"Query shape: {query[:300]}...")
    print(f"  Count: {stats['count']}")
    print(f"  Avg Time: {stats['total_time']/stats['count']:.2f}s")
    print(f"  Max Time: {stats['max_time']:.2f}s")
    print(f"  Total Rows Examined: {stats['rows_examined']}")
    if stats["timestamps"]:
        print(f"  Timestamps: {', '.join(stats['timestamps'])}")
    print()