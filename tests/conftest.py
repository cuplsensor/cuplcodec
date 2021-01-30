#  cuplcodec encodes environmental sensor data into a URL and the reverse.
#
#  https://github.com/cuplsensor/cuplcodec
#
#  Original Author: Malcolm Mackay
#  Email: malcolm@plotsensor.com
#  Website: https://cupl.co.uk
#
#  Copyright (C) 2021. Plotsensor Ltd.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import pytest
from wscodec.decoder import decode


@pytest.fixture(scope="function", params=[1, 10, 100, 1000, 1001])
def instr_sample_populated(instr_sample, request):
    inlist = instr_sample.pushsamples(request.param)

    # Decode the URL
    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = decode(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                        circb64=par['q'][0], vfmtb64=par['v'][0])

    urllist = decodedurl.get_samples_list()
    for d in urllist:
        del d['timestamp']
        del d['rawtemp']
        if 'rawrh' in d:
            del d['rawrh']

    inlist = inlist[:len(urllist)]

    return {'instr_sample': instr_sample, 'inlist': inlist, 'urllist': urllist}