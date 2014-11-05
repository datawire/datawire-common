# Analyzer
FROM centos:latest
MAINTAINER Richard Li <richard@thelis.org>

WORKDIR /tmp

# Update server
# RUN yum -y update

RUN yum -y install svn git

# required dependencies
RUN yum -y install gcc cmake libuuid-devel make

# dependencies needed for ssl support
RUN yum -y install openssl-devel

# dependencies needed for bindings
RUN yum -y install swig python-devel

# dependencies needed for java (note that any non-ancient jvm will
# work, 1.8.0 is just what is current for fedora 20)
RUN yum -y install java-1.7.0-openjdk-devel

# Proton
RUN svn co http://svn.apache.org/repos/asf/qpid/proton/trunk/
RUN cd trunk && mkdir build
WORKDIR /tmp/trunk/build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DSYSINSTALL_BINDINGS=ON -DBUILD_PHP=OFF -DBUILD_JAVA=OFF -DBUILD_RUBY=OFF -DBUILD_PERL=OFF
RUN make install

# Kinetic
RUN mkdir /opt/kinetic/
WORKDIR /opt/kinetic/
RUN git clone https://kineticbot:M6P-AqJ-UEe-bB9@bitbucket.org/gokinetic/server.git

# Set up script that is run when a container is created
ADD run-analyzer.sh /opt/kinetic/run-analyzer.sh
CMD ["/opt/kinetic/run-analyzer.sh"]