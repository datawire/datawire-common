# Kinetic Server
FROM centos:latest
MAINTAINER Richard Li <richard@thelis.org>

WORKDIR /tmp

# Get to a coherent image
RUN yum -y install tar git

# required dependencies
RUN yum -y install gcc cmake libuuid-devel

# dependencies needed for ssl support
RUN yum -y install openssl-devel

# dependencies needed for bindings
RUN yum -y install swig python-devel ruby-devel php-devel perl-devel

# dependencies needed for java (note that any non-ancient jvm will
# work, 1.8.0 is just what is current for fedora 20)
RUN yum -y install java-1.8.0-openjdk-devel

# dependencies needed for python docs
RUN yum -y install epydoc

# Proton
RUN git clone git://git.apache.org/qpid-proton.git
