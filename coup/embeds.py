from discord import Colour, Embed
from coup.cogs.mongo import Session


def session_state_label(state: str) -> str:
    if state == Session.State.WAITING:
        return 'En attente'
    elif state == Session.State.PLAYING:
        return 'En cours'
    elif state == Session.State.COMPLETED:
        return 'Terminée'
    elif state == Session.State.DESTROYED:
        return 'Supprimée'
    else:
        return state


def session_state_colour(state: str) -> Colour:
    if state == Session.State.WAITING:
        return Colour.green()
    elif state == Session.State.PLAYING:
        return Colour.orange()
    elif state == Session.State.COMPLETED:
        return Colour.red()
    elif state == Session.State.DESTROYED:
        return Colour.light_gray()
    else:
        return None


def create_game_info(session: Session) -> Embed:
    players = ['{}'.format(p.name) for p in session.players]

    embed = Embed(title='Coup - Session #{}'.format(session.id))
    embed.colour = session_state_colour(session.state)
    embed.add_field(name='Status', value=session_state_label(session.state))
    embed.add_field(name='Disponibilités', value='{} / {} joueurs'.format(len(session.players), session.max_players))
    embed.add_field(name='Liste des joueurs', value="\n".join(players), inline=False)

    return embed
