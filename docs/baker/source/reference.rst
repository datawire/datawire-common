.. _reference:

Reference
=========

Directory
---------

A single Datawire Directory allows all other Baker components to communicate.

At the command line::

  usage: directory [-h] [-c FILE] [-n HOST] [-p PORT] [-a ADDRESS] [-s STORE]
                   [-l LEVEL] [-o OUTPUT] [-V]

  optional arguments:
    -h, --help            show this help message and exit
    -c FILE, --config FILE
                          read from config file
    -n HOST, --host HOST  network host (defaults to localhost)
    -p PORT, --port PORT  network port (defaults to 5672)
    -a ADDRESS, --address ADDRESS
                          amqp address, defaults to //<host>[:<port]
    -s STORE, --store STORE
                          save routes to store
    -l LEVEL, --level LEVEL
                          logging level
    -o OUTPUT, --output OUTPUT
                          file for log output
    -V, --version         show program's version number and exit

By config file::

  [Directory]
  host: hostname-of-directory
  port: 5672
  address: //hostname-of-directory:5672
  level: WARNING
  output: filename

The ``host`` option must be set to an externally-visible hostname for the machine running the directory. It is not optional for any realistic deployment, as it defaults to ``localhost``. The ``port`` and ``address`` options are for unusual deployments only. The ``store`` option is experimental.

Output can be sent to a file, but typically the operating system's service control mechanism (systemd, Upstart, etc.) handles output redirection. The logging level may be set to ``DEBUG`` or ``INFO`` if more output is desired; ``WARNING`` is the default.

Watson
------

In a typical deployment, one microservice is deployed per server, VM, or container. Watson is deployed alongside that microservice using its configuration file and system service integration. The command line options exist to enable launching multiple instances of Watson on a single machine.

At the command line::

  usage: watson [-h] [-c FILE] [-d ADDRESS] [-l URL] address url period

  positional arguments:
    address               service address
    url                   service URL (target)
    period                seconds between liveness checks

  optional arguments:
    -h, --help            show this help message and exit
    -c FILE, --config FILE
                          read from config file (no other args)
    -d ADDRESS, --directory ADDRESS
    -l URL, --liveness URL
                          liveness check URL (default: /liveness_check under
                          service URL)

By config file::

  [Watson]
  directory: //hostname-of-directory/directory
  address: //hostname-of-directory/service-name
  url: http://localhost:9000/url/of/service
  liveness: http://localhost:9000/url/of/service/liveness_check
  period: 3  ; seconds between liveness checks

Watson connects to the liveness check URL every three seconds (as configured by the ``period`` parameter). If the service appears live (returns an HTTP response of 200), Watson ensures that the directory (as specified by the ``directory`` parameter) is aware that the indicated service (named by the ``address`` parameter) is being served at the specified URL.

Sherlock
--------

A client node, which is to say a server, VM, or container that runs software that needs to access services, runs Sherlock to enable said access. Sherlock is typically deployed using its configuration file and system service integration, but command line parameters are available to support special case usage.

At the command line::

  usage: sherlock [-h] [-c FILE] [-d ADDRESS] [-p PATH] [-r PATH]
                  [--debounce SECONDS] [--dir-debounce SECONDS]

  optional arguments:
    -h, --help            show this help message and exit
    -c FILE, --config FILE
                          read from config file (no other args)
    -d ADDRESS, --directory ADDRESS
    -p PATH, --proxy PATH
                          full path of HAProxy executable
    -r PATH, --rundir PATH
                          path to location for haproxy.{pid,conf}
    --debounce SECONDS    time in seconds to coalesce events before updating
                          HAProxy
    --dir-debounce SECONDS
                          debounce time to use when the directory has restarted

By config file::

  [Sherlock]
  directory: //hostname-of-directory/directory
  proxy: /usr/sbin/haproxy
  rundir: /opt/datawire/run
  debounce: 2
  dir_debounce: 2

Sherlock gathers information about running services and the URLs of the microservices that implement them from the directory (as specified by the ``directory`` parameter). It configures and launches HAProxy (as specified by the ``proxy`` parameter), keeping HAProxy-specific files in the path specified by the ``rundir`` parameter.

Reconfiguring HAProxy can introduce a brief interruption of service (well under a second), so Sherlock coalesces updates from the directory. When there are no new updates for two seconds (as configured by the ``debounce`` parameter in seconds), Sherlock outputs a new HAProxy configuration and reconfigures HAProxy. If Sherlock detects that it has disconnected from and then reconnected to the directory, it instead coaslesces over ``dir_debounce`` seconds.
