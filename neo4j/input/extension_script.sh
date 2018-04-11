rm -rf /var/lib/neo4j/data/databases/graph.db

nodes=`ls -d /input/nodes/*`
rels=`ls -d /input/rels/*`
nodes_str=`echo $nodes | sed "s/ / --nodes /g"`
rels_str=`echo $rels| sed "s/ / --relationships /g"`

/var/lib/neo4j/bin/neo4j-admin \
	import \
	--nodes $nodes_str \
	--relationships $rels_str \
	--delimiter ";" \
	--array-delimiter "|" \
	--multiline-fields true