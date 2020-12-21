from pkg_resources import require

from .fields import *
from .serializers import *


require('elasticsearch')
require('elasticsearch_dsl')
