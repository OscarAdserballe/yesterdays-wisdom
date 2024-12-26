# To-do list for missing functionality

* push_node_to_database in main.py: Integrating sql-lite manager with nodes, such that we push to there. there's probably a bit of redundancy right now with the fact that we have some double-storage and cleaning of cache - all that should probably be fixed in the databse. We just leverage the same logic as now, settign the primary_id as the hash
* Make sure to update the LLM agent in terms fof what needs to be done by it
* Make the whole thing async
