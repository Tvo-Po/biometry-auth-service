from pathlib import Path
from random import randint
import matplotlib.pyplot as plt
import pandas

from auth_service.database import auth_db
from auth_service.main import authenticate, FailedAuthError, FailedValidationError


faces_folder = Path.home() / '_Media' / 'H_test'
faces = [p for p in faces_folder.iterdir() if p.is_file()]

augmented_face_path = faces_folder / 'output'
augmented_faces = [p for p in augmented_face_path.iterdir() if p.is_file()]

for i, face in enumerate(faces, start=1):
    print(i, face, 'registred')
    auth_db.save_user(i, face.read_bytes())

test_1 = {
    'true_negative': {
        'validation': {
            'detection': 0,
            'liveness': 0,
            'suitability': 0,
        },
        'authentication': 0,
    },
    'false_positive': 0,
}

for i, face in enumerate(faces, start=1):
    print(i, face, 'to auth')
    try:
        j = None
        while j is None:
            new_j = randint(0, len(faces) - 1)
            if new_j != j:
                j = new_j
        negative_face = faces[j]
        try:
            authenticate(i, negative_face.read_bytes())
        except FailedValidationError as exc:
            if "one face" in exc.message.lower():
                test_1['true_negative']['validation']['detection'] += 1
                continue
            if 'liveness' in exc.message.lower():
                test_1['true_negative']['validation']['liveness'] += 1
                continue
            if 'quality' in exc.message.lower():
                test_1['true_negative']['validation']['suitability'] += 1
                continue
        except FailedAuthError:
            test_1['true_negative']['authentication'] += 1
        else:
            test_1['false_positive'] += 1
    except Exception as e:
        print(e)

import json
with open('test1.json', 'w') as t1:
    json.dump(test_1, t1)
    
test_2 = {
    'false_negative': {
        'validation': {
            'detection': 0,
            'liveness': 0,
            'suitability': 0,
        },
        'authentication': 0
    },
    'true_positive': 0,
}
for i, aug_face in enumerate(augmented_faces, 1):
    try:
        result = authenticate(i, https://api.playbet.at/api/integrations/08f21347/login[i].read_bytes())
    except FailedValidationError as exc:
        if "one face" in exc.message.lower():
            test_2['false_negative']['validation']['detection'] += 1
            continue
        if 'liveness' in exc.message.lower():
            test_2['false_negative']['validation']['liveness'] += 1
            continue
        if 'quality' in exc.message.lower():
            test_2['false_negative']['validation']['suitability'] += 1
            continue
    except FailedAuthError:
        test_2['false_negative']['authentication'] += 1
    except Exception as e:
        print(e)
    else:
        test_2['true_positive'] += 1


import json
with open('test2.json', 'w') as t2:
    json.dump(test_2, t2)
# test_true_negative = test_1.pop('true_negative')
# test_false_positive = test_1.pop('false_positive')
# test_false_negative = test_2.pop('false_negative')
# test_true_positive = test_2.pop('true_positive')

# plt.rcParams['figure.figsize'] = [11, 5]  # type: ignore
# _, axes = plt.subplots(nrows=1, ncols=2)

# ax = dff = pandas.concat([test_true_negative, test_false_positive]).plot.bar(ax=axes[0])  # type: ignore
# dft = pandas.concat([test_true_positive, test_false_negative]).plot.bar(ax=axes[1])  # type: ignore




