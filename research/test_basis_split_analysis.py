from array import array
from pathlib import Path
import tempfile
import unittest

from basis_split_analysis import checkpoint


class LinearImageReadbackTest(unittest.TestCase):
    def test_all_columns_and_stale_checkpoint_data(self):
        for mutation in ('none','column','future','padding','nan','truncated','trailing','context','temperature'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                lines = ['ordered-linear-image-checkpoint-v1; unnormalized partial sums','a'*64,'4 5 5 2 2','12.34']
                values = array('d',[0.]*20)
                values[0]=1.;values[5]=2.;values[10]=3.;values[15]=4.
                if mutation == 'column': lines[2]='4 5 5 1 2'
                if mutation == 'future': values[12]=1.
                if mutation == 'padding': lines[2]='5 4 5 2 2';values[19]=1.
                if mutation == 'nan': values[15]=float('nan')
                if mutation == 'trailing': lines.append('extra')
                if mutation == 'context': lines[1]='invalid'
                if mutation == 'temperature': lines[3]='nan'
                payload=values.tobytes()
                if mutation == 'truncated': payload=payload[:-8]
                (root/'linear-image-checkpoint.meta').write_text('\n'.join(lines)+'\n')
                (root/'linear-image-checkpoint.bin').write_bytes(payload)
                if mutation == 'none':
                    self.assertEqual(checkpoint(root)['counts'],[4,5,5,2])
                else:
                    with self.assertRaises(ValueError): checkpoint(root)
