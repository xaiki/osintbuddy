import requests
from typing import Any, List
from datetime import datetime
import urllib.parse
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.base import get_or_create
from app import crud, schemas, models
from app.api import deps

router = APIRouter(prefix='/extract')


@router.get('/breaches')
def have_i_been_pwned(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
    email: str = ""
):
    cookies = {
        '__cf_bm': 'q8kXLSEmob3vdPqNcG8K3h0NEJzI9_iSHTlAUam4rS8-1675955598-0-AZZ5wiEG/wUx99lNBq5D92N6BL/I2Ys3EyXBZdCb11HDYKweAu5CTBvrIMUwP4eHOmwzVnnaXB4t5pU8cj6ZzVT669dM5NMamzaD3oPQ9ZVLMNq3lnjgt63XlRRBHlCG82gfaN6UgRdIh+7W5StBuLLI98mr753NUjDvUmZrBVlBeGTuJnAK9fkM2/UUSNf/9w==',
        'Searches': '1',
        'BreachedSites': '0',
        'Pastes': '0',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://haveibeenpwned.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        # 'Cookie': '__cf_bm=q8kXLSEmob3vdPqNcG8K3h0NEJzI9_iSHTlAUam4rS8-1675955598-0-AZZ5wiEG/wUx99lNBq5D92N6BL/I2Ys3EyXBZdCb11HDYKweAu5CTBvrIMUwP4eHOmwzVnnaXB4t5pU8cj6ZzVT669dM5NMamzaD3oPQ9ZVLMNq3lnjgt63XlRRBHlCG82gfaN6UgRdIh+7W5StBuLLI98mr753NUjDvUmZrBVlBeGTuJnAK9fkM2/UUSNf/9w==; Searches=1; BreachedSites=0; Pastes=0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }
    response = requests.get(
        f'https://haveibeenpwned.com/unifiedsearch/{urllib.parse.unquote(email)}',
        cookies=cookies,
        headers=headers
    )
    return response.json()