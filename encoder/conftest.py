import pytest
from decoder import UrlDecoder


@pytest.fixture(scope="function", params=[1, 10, 100, 1000, 1001])
def instr_sample_populated(instr_sample, request):
    inlist = instr_sample.pushsamples(request.param)

    # Decode the URL
    par = instr_sample.eepromba.get_url_parsedqs()
    decodedurl = UrlDecoder(secretkey=instr_sample.secretkey, statb64=par['x'][0], timeintb64=par['t'][0],
                            circb64=par['q'][0], ver=par['v'][0])

    urllist = decodedurl.decoded.smpls
    for d in urllist:
        del d['ts']

    inlist = inlist[:len(urllist)]

    return {'instr_sample': instr_sample, 'inlist': inlist, 'urllist': urllist}