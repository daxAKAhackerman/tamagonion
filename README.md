# Tamagonion

## Instructions

This is Stinky, it's a Tamagonion and it's running your Tor relay. Tamagonions are cyber creatures that have bravely stepped out of the Tor network to learn what life is like in the clearnet and to help you monitor your relay. It mostly loafs around and browses the Web anonymously, but it's more entertaining than looking at a graph!

More seriously, this program is meant to help you monitor your Tor relay in a more fun way. Start Tamagonion and just let it do its thing in the corner of your desktop or in a tmux split to get a general idea of the state of your relay. It is built to have minimal dependencies, only relying on [Stem](https://stem.torproject.org/).

```
             ▌▌
             ▓▓▀
         ▄▄▄▀▀▀▀▄▄▄
        █   ─  ─   █
       █    ▄  ▄    █
      █     ▀  ▀     █
      █      ──      █
      █              █
       █▄▄▄▄▄▄▄▄▄▄▄▄█
```

## Activation

To activate the viewport, use the `tamagonion` command as such:

```bash
# Install tamagonion
# If you'd rather run it directly from this repository, you can use `uv run tamagonion` instead
$ pip install tamagonion

# By default, we will try to connect to the control port at 127.0.0.1:9051
$ tamagonion

# If you use password authentication, you can supply it with -P or with the TAMAGONION_PASSWORD environment variable
$ tamagonion -P my_password
$ TAMAGONION_PASSWORD=my_password tamagonion

# If the port is listening somewhere else, you can specify it with -i and -p
$ tamagonion -i 192.168.0.10 -p 9999

# If you are connecting using a Unix socket, you can point to it with -s
$ tamagonion -s /var/run/tor/control
```

## Home screen

```
┌──────────────────────────────────────────────┐
│Relay nickname: exitigefkebk                  │
│Uptime: 0d 06h 08m 09s                        │
│Connections (N/L/Co/F/Cl): 0/0/6/0/0          │
│Download (Cur/Avg/Tot): 338B / 97B / 2MB      │
│Upload (Cur/Avg/Tot): 1KB / 92B / 2MB         │
│Version: 0.4.9.11                             │
│                                              │
│                              ░░░░░░░░        │
│                             ░╔══════╗░   █▄  │
│             ▌▌          z   ░║ EXIT ║░ █████ │
│             ▓▓▀        Z    ░╚══════╝░   █▀  │
│         ▄▄▄▀▀▀▀▄▄▄   Z       ░░░░░░░░        │
│        █   ─  ─    ▄▄▄▄▄                     │
│       █           █  █  █                    │
│      █    ──  ── █  ▀█▀  █  ╓───┬───╖╤═══╕   │
│ ____ █      ∙     █  █  █   ║---│---║╧╤══╧╤  │
││oV2o│█             ▀▀▀▀▀    ║---│---║╒╧══╤╧  │
│╘════╛ █▄▄▄▄▄▄▄▄▄▄▄▄█        ╙───┴───╜╘═══╧   │
└───────────────────────|Home│Status│Hints│Quit┘
```

The top of the viewport contains various information about your relay. More specifically:

- The relay nickname as defined in your Tor configuration
- The uptime since the Tor daemon has started
- The number of connections
  - NEW: We have received a new incoming OR connection, and are starting the server-side handshake
  - LAUNCHED: We have launched a new outgoing OR connection, and are starting the client-side handshake
  - CONNECTED: The OR connection has been connected and the handshake is done
  - FAILED: Our attempt to open the OR connection failed
  - CLOSED: The OR connection closed in an unremarkable way
- The current, average and total amount of data that was downloaded and uploaded
- The version of the Tor binary

You can always come back home by pressing `H`, and quit the app using `Q`.

## Biology

Tamagonions are very attuned to a relay's operation. You can know how your relay is going by looking at how Stinky is feeling or behaving.

| Behaviour    | Meaning                                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------- |
| Sad          | The relay doesn't have the both the "Valid" and the "Running" flags, or it has the "NoEdConsensus" flag.                  |
| Confused     | The relay discarded expired statuses and server descriptors to fall below the desired threshold of directory information. |
| Embarrassed  | A directory authority rejected our descriptor.                                                                            |
| Looking away | The relay's ORPort is unreachable.                                                                                        |
| Bored        | The relay has the "MiddleOnly" flag.                                                                                      |
| Glitchy      | The relay doesn't have the "Stable" flag.                                                                                 |
| Old          | The relay has the "StaleDesc" flag.                                                                                       |
| Egg          | The relay is bootstrapping.                                                                                               |
| Slow         | The relay doesn't have the "Fast" flag.                                                                                   |
| Hurt         | The Tor binary version is either obsolete, unrecommended or unknown.                                                      |
| Asleep       | This just means that it's bed time for Stinky. What, you expected it to never sleep?                                      |

## Room status check

Stinky's room can get a bit crowded with things it collected along the way. But everything it collects means something special to it.

| Object or room state | Meaning                                        |
| -------------------- | ---------------------------------------------- |
| Light's out          | The relay believes the network is unreachable. |
| Exit sign            | The relay has the "Exit" flag.                 |
| Broken exit sign     | The relay has the "BadExit" flag.              |
| Books                | The relay has the "HSDir" flag.                |
| Cassette             | The relay has the "V2Dir" flag.                |
| Shield               | The relay has the "Guard" flag.                |

## Status check

To get an explanation of Stinky's state, press `S` and you will be shown details about the reason behind its behaviour.

```
┌──────────────────────────────────────────────┐
│┌Status──────────────────────────────────────┐│
││Dormant: Yes                                ││
││Network liveness: Live                      ││
││Bootstrap progress: 100%                    ││
││Enough directory info: Yes                  ││
││Good server descriptor: Yes                 ││
││Reachability: Reachable                     ││
││Version status: none recommended            ││
││Flags: Exit, Fast, Guard, HSDir, Running    ││
││       V2Dir, Valid                         ││
││                                            ││
││                                            ││
││                                            ││
││                                            ││
││                                            ││
││                                            ││
││                                            ││
│└────────────────────────────────────────────┘│
└───────────────────────|Home│Status│Hints│Quit┘
```

## Adjusting the viewport

Here are a few examples of how you could typically launch Tamagonion:

```bash
# If you are using Kitty, you can start a new terminal running only tamagonion with the correct dimensions
$ TAMAGONION_PASSWORD=my_password kitty --override remember_window_size=no --override initial_window_width=48c --override initial_window_height=20c tamagonion

# If you are using tmux, you can add a bind as such to create a popup that will quickly show you tamagonion
echo 'bind-key T display-popup -E -w 50 -h 22 -x R -y S -- env TAMAGONION_PASSWORD=my_password /home/user/.pyenv/shims/tamagonion' >> ~/.tmux.conf

# Or if you want a permanent split
pane=$(tmux split-window -h -d -l 48 -P -F '#{pane_id}'); tmux split-window -v -d -l 20 -t "$pane" env TAMAGONION_PASSWORD=my_password tamagonion
```

## You may also like...

- [Testing Tor Network](https://github.com/daxAKAhackerman/testing-tor-network) - CLI tool to setup a testing TOR network with Docker
- [Tor HashedControlPassword Brute](https://github.com/daxAKAhackerman/tor-hashed-control-password-brute) - C program to execute a dictionary attack against a Tor HashedControlPassword value

---

> This repository contains no AI-generated code and was made with :heart: by [@daxAKAhackerman](https://github.com/daxAKAhackerman/)
