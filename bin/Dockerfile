# Analyzer
FROM centos:latest
MAINTAINER Richard Li <richard@thelis.org>

# Update server
RUN yum -y update
RUN yum -y install git

# required dependencies
RUN yum -y install gcc cmake libuuid-devel make 

# dependencies needed for ssl support
RUN yum -y install openssl-devel

# dependencies needed for bindings
RUN yum -y install swig python-devel

# dependencies needed for java (note that any non-ancient jvm will
# work, 1.8.0 is just what is current for fedora 20)
RUN yum -y install java-1.7.0-openjdk-devel


WORKDIR /tmp

# Proton
RUN git clone https://git-wip-us.apache.org/repos/asf/qpid-proton.git
RUN cd qpid-proton && mkdir build
WORKDIR /tmp/qpid-proton/build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DSYSINSTALL_BINDINGS=ON -DBUILD_PHP=OFF -DBUILD_JAVA=OFF -DBUILD_RUBY=OFF -DBUILD_PERL=OFF
RUN make install

# Kinetic
RUN mkdir /opt/kinetic/
WORKDIR /opt/kinetic/
RUN git clone https://kineticbot:M6P-AqJ-UEe-bB9@bitbucket.org/gokinetic/server.git

# Start analyzer
ENTRYPOINT ["/opt/kinetic/server/analyzer"]
