import library.clients.entityclient as entityclient

ec = entityclient.EntityClient()


def test_entity_by_tags_payload():
    tags_arr = ["owner:John Smith", "Team:Acme Team"]
    payload = entityclient.EntityClient._entity_by_tag_payload(tags_arr)
    print(payload)


test_entity_by_tags_payload()