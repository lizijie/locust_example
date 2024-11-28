import os
from pysproto.sprotoparser import Convert, flattypename
from pysproto import parse_ast, Sproto

SPROTO = None
SPROTO_MSG = None

def parse_list(sproto_list):
    build = {"protocol": {}, "type": {}}
    for v in sproto_list:
        ast = Convert.parse(v[0], v[1])

        # merge type
        for stname, stype in ast["type"].items():
            assert stname not in build["type"], "redifine type %s in %s" % (
                stname,
                v[1],
            )
            build["type"][stname] = stype
        # merge protocol
        for spname, sp in ast["protocol"].items():
            assert (
                spname not in build["protocol"]
            ), "redifine protocol name %s in %s" % (spname, v[1])
            for proto in build["protocol"]:
                assert (
                    sp["tag"] != build["protocol"][proto]["tag"]
                ), "redifine protocol tag %d in %s with %s" % (sp["tag"], proto, spname)
            build["protocol"][spname] = sp

    flattypename(build)
    # checkprotocol(build)
    return build


def load_protos(src_dir):
    global SPROTO, SPROTO_MSG

    if SPROTO is not None and SPROTO_MSG is not None:
        print("return")
        return SPROTO, SPROTO_MSG

    sproto_list = []
    for f in os.listdir(src_dir):
        file_path = os.path.join(src_dir, f)
        if os.path.isfile(file_path) and f.endswith(".sproto"):
            text = open(file_path, encoding="utf-8").read()
            sproto_list.append((text, f))
    build = parse_list(sproto_list)
    dump = parse_ast(build)
    SPROTO = Sproto(dump)
    SPROTO_MSG = SPROTO.querytype("Msg")

def clean_protos():
    SPROTO = None
    SPROTO_MSG = None

def sproto_query(name:str):
    return SPROTO.querytype(name)

def sproto_encode(name:str, pkg:dict):
    tp = SPROTO.querytype(name)
    return SPROTO_MSG.encode({
            "Name":name,
            "Bin": tp.encode(pkg),
    })

def sproto_decode(bytes):
    msg_pkg = SPROTO_MSG.decode(bytes)
    name = msg_pkg["Name"]
    proto_meta = SPROTO.querytype(name)
    pkg = proto_meta.decode(msg_pkg["Bin"])
    return name, pkg
