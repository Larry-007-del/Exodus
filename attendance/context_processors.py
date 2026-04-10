"""
Context processors for the Exodus Attendance System.
"""


def user_avatar(request):
    """Inject avatar metadata for the authenticated user into every template.

    Returns:
        avatar_initials:  1–2 letter string (e.g. "JD" for John Doe)
        avatar_color:     Tailwind colour class for the avatar background
    """
    if not request.user.is_authenticated:
        return {}

    # Build initials
    first = (request.user.first_name or '').strip()
    last = (request.user.last_name or '').strip()
    if first and last:
        initials = (first[0] + last[0]).upper()
    elif first:
        initials = first[:2].upper()
    elif request.user.username:
        initials = request.user.username[:2].upper()
    else:
        initials = 'U'

    # Deterministic colour from username hash (10 warm/cool palette options)
    COLOURS = [
        'bg-indigo-500',
        'bg-purple-500',
        'bg-blue-500',
        'bg-emerald-500',
        'bg-teal-500',
        'bg-rose-500',
        'bg-amber-500',
        'bg-cyan-500',
        'bg-fuchsia-500',
        'bg-lime-500',
    ]
    colour = COLOURS[hash(request.user.username) % len(COLOURS)]

    return {
        'avatar_initials': initials,
        'avatar_color': colour,
    }
