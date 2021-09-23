#!/usr/bin/env python3
import dataclasses
import datetime
import json
import logging
import progressbar
import psycopg2.extras
import typing as tp

from decode import get_secret_object, decode_choice


@dataclasses.dataclass
class VoteTransaction:
    hash: str
    datetime: datetime.datetime
    district_id: int
    decrypted_choice: int
    decoded_choice: str
    decrypted_in_dump: bool

    def as_json(self) -> dict:
        return {
            "hash": self.hash, "datetime": self.datetime.strftime("%Y%m%d-%H:%M:%S"), "district_id": self.district_id,
            "decrypted_choice": self.decrypted_choice, "decoded_choice": self.decoded_choice, "decrypted_in_dump": self.decrypted_in_dump
        }


def get_private_key(connection: psycopg2.extensions.connection) -> str:
    with connection.cursor(cursor_factory = psycopg2.extras.DictCursor) as cur:
        cur.execute("select hash, payload from public.transactions where method_id = 8")
        return next(iter(cur))['payload']['private_key']


def get_vote_description(connection: psycopg2.extensions.connection) -> dict:
    with connection.cursor(cursor_factory = psycopg2.extras.DictCursor) as cur:
        cur.execute("select hash, payload from transactions where method_id = 0")
        return next(iter(cur))['payload']


def get_decoded_voices(connection: psycopg2.extensions.connection) -> tp.Iterable[VoteTransaction]:
    private_key = get_private_key(connection)
    vote_description = get_vote_description(connection)
    sKey = get_secret_object(private_key)
    with connection.cursor(cursor_factory = psycopg2.extras.DictCursor) as cur:
        cur.execute("select status, store_tx_hash, decrypted_choice from public.decrypted_ballots")
        decrypted_ballots = {rec['store_tx_hash']: rec['decrypted_choice'][0] for rec in cur if rec['status'] == 'Valid'}
    with connection.cursor(cursor_factory = psycopg2.extras.DictCursor) as cur:
        cur.execute("select hash, datetime, payload from public.transactions where method_id = 6 order by datetime")
        for rec in cur:
            enc = rec['payload']['encrypted_choice']
            try:
                district_id = rec['payload']['district_id']
                decrypted_in_dump = rec['hash'] in decrypted_ballots
                decrypted_choice = decode_choice(enc['encrypted_message'], enc['nonce'], enc['public_key'], sKey)[0]
                if decrypted_in_dump:
                    assert decrypted_ballots[rec['hash']] == decrypted_choice
                decoded_choice = decode_choice_option(vote_description, district_id, decrypted_choice)
                yield VoteTransaction(rec['hash'], rec['datetime'], district_id, decrypted_choice, decoded_choice, decrypted_in_dump)
            except Exception as e:
                logging.warning(f"can't decrypt transaction with hash = {rec['hash']}: {e}")


def decode_choice_option(vote_description, district_id, choice):
    ballot_idx = district_id - vote_description['ballots_config'][0]['district_id']
    district_description = vote_description['ballots_config'][ballot_idx]
    assert district_description['district_id'] == district_id
    return district_description['options'][str(choice)]


if __name__ == "__main__":
    db_name = "moscow2021"
    db_user = 'postgres'
    db_password = 'wee5ahLae5Ut'
    connection = psycopg2.connect(host="127.0.0.1", port=5432, database="moscow2021", password="wee5ahLae5Ut", user="postgres")
    with open("votes-dump.json", "w") as votes_printer:
        for vote in progressbar.ProgressBar()(get_decoded_voices(connection)):
            print(json.dumps(vote.as_json(), ensure_ascii=False), file=votes_printer)
