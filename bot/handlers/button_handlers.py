from abc import ABC
import copy
from typing import Any, Tuple

from telegram import InlineKeyboardButton
import yaml

from bot.models import BotChatUser, Subscription
from .boardroom_api_client import BroadroomAPIClient
from .utils import TgUrl

DASH_LINE = "_" * 30


class TgResponse:
    keyboards: list
    message: str

    def __init__(self, message: str, keyboards: list = None) -> None:
        self.message = message
        self.keyboards = keyboards


class TgView(ABC):
    def __init__(self, chat_ids: list) -> None:
        self.msg = ""
        self.keyboards = []
        self.api_client = BroadroomAPIClient()
        self.chat_id = None
        if len(chat_ids) > 0:
            self.chat_id = chat_ids[0]
        self.chat_ids = chat_ids

    def load_data(self, url: TgUrl, next_cursor: str):
        pass

    def execute(self, url: TgUrl) -> TgResponse:
        data = self.load_data(url, next_cursor=url.queries.get("next", None))
        return self.render(url, data)

    def render(self, url: TgUrl, data: Any) -> TgResponse:
        # escape invalid telegram chars.
        self.msg = (
            self.msg.replace("_", "\\_").replace("[", "\\[").replace("`", "\\`")
        )  # .replace("*", "\\*") \

        back_url = self.back_url(url, data)
        if back_url is not None:
            self.keyboards += [
                [InlineKeyboardButton("Back", callback_data=self.back_url(url, data))],
            ]
        return TgResponse(self.msg, self.keyboards)

    def back_url(self, url: TgUrl, data: Any):
        return None

    def to_message(self, dictionary):
        return yaml.dump(dictionary, sort_keys=False)


class PaginatedTgView(TgView):
    def render(self, url: TgUrl, data: Any) -> TgResponse:
        resp = super().render(url, data)

        # Place the more button before the back button if present.
        placement = len(resp.keyboards) - 1
        if placement == -1:
            placement = 0

        next, exists = self.next_url(url, data)
        if exists:
            resp.keyboards.insert(
                placement,
                [InlineKeyboardButton("First page", callback_data=self.fist_url(url).get())],
            )
            resp.keyboards.insert(
                placement,
                [InlineKeyboardButton("Next page", callback_data=next.get())],
            )
        return resp

    def next_url(self, url: TgUrl, data: Any) -> Tuple[TgUrl, bool]:
        next_url = copy.deepcopy(url)
        exists = False
        if "nextCursor" in data:
            next_url.queries["next"] = data["nextCursor"]
            exists = True
        return next_url, exists

    def fist_url(self, url: TgUrl) -> TgUrl:
        first_url = copy.deepcopy(url)
        first_url.queries.pop("next", None)
        return first_url

    def to_message(self, dictionary):
        return yaml.dump(dictionary, sort_keys=False)


class SubscriptionsTgView(TgView):
    IDENTIFIER = "subscriptions"

    def load_data(self, url: TgUrl, next_cursor: str):
        return Subscription.objects.filter(user__user_id=self.chat_id)

    def render(self, url: TgUrl, data: Any):
        self.msg = f"*Subscription*\n{DASH_LINE}\n\n"
        if len(data) > 0:
            for sub in data:
                self.keyboards.append(
                    [
                        InlineKeyboardButton(
                            sub.proposal_title,
                            callback_data=TgUrl(
                                ProposalDetailTgView.IDENTIFIER, {"refId": sub.ref_id}
                            ).get(),
                        )
                    ],
                )
        else:
            self.msg = "No subscriptions found!"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl("start", {}).get()


class SubscribeTgView(TgView):
    IDENTIFIER = "subscribe"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_single_proposal(url.queries["refId"])

    def render(self, url: TgUrl, data: Any):
        if "data" in data:
            user = BotChatUser.objects.filter(user_id=self.chat_id)
            if len(user) == 1:
                sub, _ = Subscription.objects.get_or_create(
                    user_id=user[0].id,
                    ref_id=url.queries["refId"],
                    protocol=data["data"]["protocol"],
                    proposal_title=data["data"]["title"],
                )
                self.msg = f"Subscribed to {data['data']['title']}"
            else:
                self.msg = "An error happend"
        else:
            self.msg = "An error happend"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl(ProposalDetailTgView.IDENTIFIER, url.queries).get()


class UnsubscribeTgView(TgView):
    IDENTIFIER = "unsubscribe"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_single_proposal(url.queries["refId"])

    def render(self, url: TgUrl, data: Any):
        if "data" in data:
            Subscription.objects.filter(
                user__user_id=self.chat_id, ref_id=url.queries["refId"]
            ).delete()
            self.msg += f"Unsubscribed from *{data['data']['title']}*"
        else:
            self.msg = "An error happend"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl(ProposalDetailTgView.IDENTIFIER, url.queries).get()


class ProtocolsTgView(PaginatedTgView):
    IDENTIFIER = "protocols"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_protocols_cached(next_cursor)

    def render(self, url: TgUrl, data: Any):
        self.msg = f"*Protocols* (sorted by name)\n{DASH_LINE}\n\n"
        if "data" in data:
            for protocol in data["data"]:
                self.keyboards.append(
                    [
                        InlineKeyboardButton(
                            protocol["name"],
                            callback_data=TgUrl(
                                ProtocolDetailTgView.IDENTIFIER, {"protocol": protocol["cname"]}
                            ).get(),
                        )
                    ],
                )
        else:
            self.msg = "Some error happend from api side"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl("start", {}).get()

    def to_message(self, dictionary):
        data = {k: v for k, v in dictionary.items() if k not in ["icons", "protocol"]}
        yaml_str = yaml.dump(data, sort_keys=False)
        # Adding a large icon to the response
        if "icons" in dictionary:
            yaml_str += "\n" + dictionary["icons"][-1]["url"]
        return yaml_str


class TopProtocolsTgView(TgView):
    IDENTIFIER = "top_protocols"

    def load_data(self, url: TgUrl, next_cursor: str):
        return Subscription.top_protocols()

    def render(self, url: TgUrl, data: Any):
        self.msg = f"*Top protocols* (sorted by name)\n{DASH_LINE}\n\n"
        if len(data) > 0:
            for protocol in data:
                self.keyboards.append(
                    [
                        InlineKeyboardButton(
                            protocol,
                            callback_data=TgUrl(
                                ProtocolDetailTgView.IDENTIFIER, {"protocol": protocol}
                            ).get(),
                        )
                    ],
                )
        else:
            self.msg = "List is empty"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl("start", {}).get()


class TopProposalsTgView(TgView):
    IDENTIFIER = "top_proposals"

    def load_data(self, url: TgUrl, next_cursor: str):
        return Subscription.top_proposals()

    def render(self, url: TgUrl, data: Any):
        self.msg = f"*Top proposals* (sorted by name)\n{DASH_LINE}\n\n"
        if len(data) > 0:
            for name, ref_id in data.items():
                self.keyboards.append(
                    [
                        InlineKeyboardButton(
                            name,
                            callback_data=TgUrl(
                                ProposalDetailTgView.IDENTIFIER, {"refId": ref_id}
                            ).get(),
                        )
                    ],
                )
        else:
            self.msg = "List is empty"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl("start", {}).get()


class ProtocolDetailTgView(TgView):

    IDENTIFIER = "pdetail"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_single_protocol_cached(url.queries["protocol"])

    def render(self, url: TgUrl, data: Any):
        self.msg = f"Protocol details for: *{url.queries['protocol']}*\n{DASH_LINE}\n\n"
        if "data" in data:
            currentProtocol = data["data"]
            self.msg += self.to_message(currentProtocol)
        else:
            self.msg = "Some error happend from api side"
        self.keyboards += [
            [
                InlineKeyboardButton(
                    "Active proposals",
                    callback_data=TgUrl(
                        ProtocolProposalsTgView.IDENTIFIER,
                        {"protocol": url.queries["protocol"], "state": "active"},
                    ).get(),
                )
            ],
            [
                InlineKeyboardButton(
                    "Queued proposals",
                    callback_data=TgUrl(
                        ProtocolProposalsTgView.IDENTIFIER,
                        {"protocol": url.queries["protocol"], "state": "queued"},
                    ).get(),
                )
            ],
            [
                InlineKeyboardButton(
                    "Executed proposals",
                    callback_data=TgUrl(
                        ProtocolProposalsTgView.IDENTIFIER,
                        {"protocol": url.queries["protocol"], "state": "executed"},
                    ).get(),
                )
            ],
            [
                InlineKeyboardButton(
                    "Canceled proposals",
                    callback_data=TgUrl(
                        ProtocolProposalsTgView.IDENTIFIER,
                        {"protocol": url.queries["protocol"], "state": "canceled"},
                    ).get(),
                )
            ],
            [
                InlineKeyboardButton(
                    "Voters",
                    callback_data=TgUrl(
                        ProtocolVotersTgView.IDENTIFIER, {"protocol": url.queries["protocol"]}
                    ).get(),
                )
            ],
        ]
        return super().render(url, data)

    def to_message(self, dictionary):
        if "icons" in dictionary:
            out = {k: v for k, v in dictionary.items() if k not in ["icons"]}
            yaml_str = yaml.dump(out, sort_keys=False)
            yaml_str += "\n\n" + dictionary["icons"][-1]["url"]
        else:
            yaml_str = yaml.dump(dictionary, sort_keys=False)
        return yaml_str

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl(ProtocolsTgView.IDENTIFIER, {}).get()


class ProtocolProposalsTgView(PaginatedTgView):

    IDENTIFIER = "protocolproposals"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_protocol_proposals_cached(url.queries["protocol"], next_cursor)

    def render(self, url: TgUrl, data: Any):
        cname = url.queries["protocol"]
        requested_state = url.queries["state"]
        self.msg = f"Proposals for *{cname}* \n"
        if "data" in data:
            for proposal in data["data"]:
                if proposal["currentState"] == requested_state:
                    self.keyboards.append(
                        [
                            InlineKeyboardButton(
                                proposal["title"],
                                callback_data=TgUrl(
                                    ProposalDetailTgView.IDENTIFIER, {"refId": proposal["refId"]}
                                ).get(),
                            )
                        ],
                    )
        else:
            self.msg = "Oops there is a problem"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl(ProtocolDetailTgView.IDENTIFIER, url.queries).get()


class ProposalDetailTgView(TgView):

    IDENTIFIER = "refid"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_single_proposal_cached(url.queries["refId"])

    def render(self, url: TgUrl, data: Any):
        self.msg = f"Proposal details for:\n*{url.queries['refId']}*\n{DASH_LINE}\n\n"
        current_state = ""
        if "data" in data:
            self.msg += f"{self.to_message(data['data'])} \n"
            current_state = data["data"]["currentState"]
        else:
            self.msg = "Oops there is a problem"

        # We want to subscribe on live proposals.
        if current_state in ["active", "queued"]:
            if Subscription.objects.filter(
                user__user_id=self.chat_id, ref_id=url.queries["refId"]
            ).exists():
                self.keyboards += [
                    [
                        InlineKeyboardButton(
                            "Unsubscribe",
                            callback_data=TgUrl(
                                UnsubscribeTgView.IDENTIFIER, {"refId": url.queries["refId"]}
                            ).get(),
                        )
                    ],
                ]
            else:
                self.keyboards += [
                    [
                        InlineKeyboardButton(
                            "Subscribe",
                            callback_data=TgUrl(
                                SubscribeTgView.IDENTIFIER, {"refId": url.queries["refId"]}
                            ).get(),
                        )
                    ],
                ]
        self.keyboards += [
            [
                InlineKeyboardButton(
                    "Vote",
                    callback_data=TgUrl(
                        ProposalVotesTgView.IDENTIFIER, {"refId": url.queries["refId"]}
                    ).get(),
                )
            ],
        ]
        return super().render(url, data)

    def to_message(self, dictionary):
        dictionary = {
            k: v
            for k, v in dictionary.items()
            if k
            in [
                "title",
                "protocol",
                "proposer",
                "totalVotes",
                "currentState",
                "choices",
                "results",
            ]
        }
        return yaml.dump(dictionary, sort_keys=False)

    def back_url(self, url: TgUrl, data: Any):

        if "state" in url.queries:
            return TgUrl(ProtocolProposalsTgView.IDENTIFIER, url.queries).get()
        return TgUrl("start", {}).get()


class ProposalVotesTgView(PaginatedTgView):
    IDENTIFIER = "proposalvotes"

    def load_data(self, url: TgUrl, next_cursor: str):
        print(next_cursor)
        return self.api_client.get_proposal_votes_cached(url.queries["refId"], next_cursor)

    def render(self, url: TgUrl, data: Any):
        self.msg = f"Proposal votes for ref_id:\n*{url.queries['refId']}* \n\n"
        if "data" in data:
            for vote in data["data"]:
                self.msg += f"{self.to_message(vote)} \n"
                self.msg += f"{DASH_LINE}\n"
        else:
            self.msg = "Oops there is a problem"
        return super().render(url, data)

    def to_message(self, dictionary):
        dictionary = {
            k: v
            for k, v in dictionary.items()
            if k in ["proposalId", "protocol", "power", "choice"]
        }
        return yaml.dump(dictionary, sort_keys=False)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl(ProposalDetailTgView.IDENTIFIER, url.queries).get()


class VotersByAddressTgView(TgView):
    """The voter address should be included here."""

    IDENTIFIER = "voteraddress"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_votes_by_voters_cached(url.queries["address"], next_cursor)

    def render(self, url: TgUrl, data: Any):
        self.msg = f"Voter votes for voter:\n*{url.queries['address']}* \n\n"
        if "data" in data:
            for voter in data["data"]:
                self.msg += f"{self.to_message(voter)} \n"
                self.msg += f"{DASH_LINE}\n"
        else:
            self.msg = "Oops there is a problem"
        return super().render(url, data)

    def to_message(self, dictionary):
        dictionary = {
            k: v
            for k, v in dictionary.items()
            if k in ["proposalId", "protocol", "power", "choice"]
        }
        return yaml.dump(dictionary, sort_keys=False)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl(VoterDetailTgView.IDENTIFIER, url.queries).get()


class ProtocolVotersTgView(PaginatedTgView):

    IDENTIFIER = "protocolvoters"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_protocol_voters_cached(url.queries["protocol"], next_cursor)

    def render(self, url: TgUrl, data: Any):
        self.msg = f"Protocol voters for: *{url.queries['protocol']}*\n{DASH_LINE}\n\n"
        if "data" in data:
            for voter in data["data"]:
                self.keyboards.append(
                    [
                        InlineKeyboardButton(
                            voter["address"],
                            callback_data=TgUrl(
                                VoterDetailTgView.IDENTIFIER,
                                {"address": voter["address"], "protocol": url.queries["protocol"]},
                            ).get(),
                        )
                    ],
                )
        else:
            self.msg = "Oops there is a problem"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl(ProtocolDetailTgView.IDENTIFIER, url.queries).get()


class VotersTgView(PaginatedTgView):

    IDENTIFIER = "voters"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_voters_cached(next_cursor)

    def render(self, url: TgUrl, data: Any):
        self.msg = f"*Voters*\n{DASH_LINE}\n\n"
        if "data" in data:
            for voter in data["data"]:
                self.keyboards.append(
                    [
                        InlineKeyboardButton(
                            voter["address"],
                            callback_data=TgUrl(
                                VoterDetailTgView.IDENTIFIER, {"address": voter["address"]}
                            ).get(),
                        )
                    ],
                )
        else:
            self.msg = "Oops there is a problem"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl("start", {}).get()


class VoterDetailTgView(TgView):

    IDENTIFIER = "votersdetail"

    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_single_voter_cached(url.queries["address"])

    def render(self, url: TgUrl, data: Any):
        self.msg = f"*Voter details*\n{DASH_LINE}\n\n"
        if "data" in data:
            voter = data["data"]
            self.msg += f"{self.to_message(voter)} \n"
        else:
            self.msg = "Oops there is a problem"
        self.keyboards += [
            [
                InlineKeyboardButton(
                    "Votes",
                    callback_data=TgUrl(
                        VotersByAddressTgView.IDENTIFIER, {"address": url.queries["address"]}
                    ).get(),
                )
            ],
        ]
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        if "protocol" in url.queries:
            return TgUrl(
                ProtocolVotersTgView.IDENTIFIER, {"protocol": url.queries["protocol"]}
            ).get()
        return TgUrl(VotersTgView.IDENTIFIER, {}).get()


class StatTgView(TgView):
    def load_data(self, url: TgUrl, next_cursor: str):
        return self.api_client.get_stat()

    def render(self, url: TgUrl, data: Any):
        if "data" in data:
            stats = data["data"]
            self.msg += f"{self.to_message(stats)} \n"
        else:
            self.msg = "Oops there is a problem"
        return super().render(url, data)

    def back_url(self, url: TgUrl, data: Any):
        return TgUrl("start", {}).get()


class MessageTgView(TgView):
    def render(self, url: TgUrl, data: Any):
        self.msg = url.queries["message"]
        return super().render(url, data)
