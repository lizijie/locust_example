from users.game_user import GameUser
from common.sproto_utils import load_protos
from locust import events

@events.init_command_line_parser.add_listener
def init_command_line_parser(parser):
    parser.add_argument("--my-protos-path", type=str, env_var="MY_PROTOS_PATH", default="../protos", include_in_web_ui=True, help="My protos path")
    parser.add_argument("--my-mods-path", type=str, env_var="MY_MODS_PATH", default="./mods", include_in_web_ui=True, help="My mods path")

@events.init.add_listener
def init(environment, **kw):
    load_protos(environment.parsed_options.my_protos_path)
