from via_common.util.helper import dict2obj, json2obj, generate_unique_id, json2dict


def test_dict2obj():
    data = {'A': 'B'}
    res = dict2obj(data)
    assert isinstance(res, tuple)
    assert res.A == 'B'


def test_json2obj():
    data = '{"A":"B"}'
    res = json2obj(data)
    assert isinstance(res, tuple)
    assert res.A == 'B'


def test_obj2dict():
    data = json2obj('{"A":"B", "C": [{"D":"E"}, {"F":"G"}], "H":{"I":"J"}}')
    res = json2dict(data)
    assert isinstance(res, dict)
    assert res['A'] == 'B'
    assert res['C'] == [{'D': 'E'}, {'F': 'G'}]
    assert res['H'] == {'I': 'J'}


def test_generate_unique_id():
    res1 = generate_unique_id()
    res2 = generate_unique_id()
    assert len(res1) == 36 and len(res2) == 36 and res1 != res2
