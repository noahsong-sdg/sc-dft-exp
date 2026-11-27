import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import digest
from stage_band_serialization import stage
from stage_public_band_pilot import NAMES
from verify_band_serialization import verify


class BandSerializationTest(unittest.TestCase):
    def test_owning_writer_readback_checks_all_bands_weights_and_immutable_copies(self):
        self.check_grid(48)

    def test_explicit64_writer_and_readback(self):
        self.check_grid(64)

    def test_explicit32_writer_and_readback(self):
        self.check_grid(32)

    def check_grid(self, grid):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();bands=root/'bands';save=bands/'scratch/pwscf.save';save.mkdir(parents=True)
            rows=[dict(k_tpiba=[i/1000.,0.,0.],eigenvalues_ry=[float(j) for j in range(26)]) for i in range(100)]
            xml='<root><output><band_structure>'+''.join('<ks_energies><k_point weight=".02">'+
                ' '.join(map(str,r['k_tpiba']))+'</k_point><eigenvalues>'+
                ' '.join(str(x/2) for x in r['eigenvalues_ry'])+'</eigenvalues></ks_energies>' for r in rows)+'</band_structure></output></root>'
            for name in NAMES:
                (save/name).write_text(xml if name.endswith('.xml') else 'original')
            (bands/'reference.json').write_text(json.dumps(rows))
            parent_manifest=bands/'manifest.json';command=[str(bands/'pw.x')]
            parent_manifest.write_text(json.dumps(dict(cwd=str(bands),grid=[grid]*3,command=command,
                files=[dict(path=str(save/'charge-density.dat'),bytes=8,sha256=digest(save/'charge-density.dat'))])))
            receipt=bands/'results/bands/receipt.json';receipt.parent.mkdir(parents=True)
            receipt.write_text(json.dumps(dict(status='FAIL',error='failed',exit=1,command=command,cwd=str(bands),continuous_deadline_s={32:600,48:1200,64:1800}[grid])))
            exe=root/'source.x';exe.write_text('serializer')
            with self.assertRaisesRegex(ValueError,'did not pass'):
                stage(exe,bands,parent_manifest,root/'failed',grid=grid)
            self.assertFalse((root/'failed').exists())
            receipt.write_text(json.dumps(dict(status='PASS',error=None,exit=0,command=command,cwd=str(bands),continuous_deadline_s={32:600,48:1200,64:1800}[grid])))
            run=root/'serialization';manifest=stage(exe,bands,parent_manifest,run,grid=grid)
            terminal=run/'results/serialize/receipt.json';terminal.parent.mkdir(parents=True)
            terminal.write_text(json.dumps(dict(status='PASS',error=None,exit=0,command=manifest['command'],cwd=str(run),continuous_deadline_s=120)))
            text=('26 100\n'+' '.join(str(x) for r in rows for x in r['eigenvalues_ry'])+'\n'+
                ' '.join(str(x) for r in rows for x in r['k_tpiba'])+'\n'+' '.join(['.02']*100)+'\n'+f'{grid} {grid} {grid}\n')
            output=run/'scratch/pwscf.a2Fsave';output.write_text(text)
            result=verify(run,run/'run-manifest.json',grid=grid)
            self.assertTrue(result['shared_point_and_serialization_targets_met'])
            if grid!=48:
                with self.assertRaisesRegex(ValueError,'Changed declared'):
                    verify(run,run/'run-manifest.json')
                with self.assertRaisesRegex(ValueError,'Expected declared48'):
                    stage(exe,bands,parent_manifest,root/'wrong-default')
                self.assertFalse((root/'wrong-default').exists())
            self.assertFalse(result['original_output_protocol_pass'])
            energy=text.splitlines();values=energy[1].split();values[-1]='25.01';energy[1]=' '.join(values)
            output.write_text('\n'.join(energy)+'\n')
            with self.assertRaisesRegex(ValueError,'does not preserve'):
                verify(run,run/'run-manifest.json',grid=grid)
            changed=text.splitlines();weights=changed[3].split();weights[:2]=['.019','.021'];changed[3]=' '.join(weights)
            output.write_text('\n'.join(changed)+'\n')
            with self.assertRaisesRegex(ValueError,'does not preserve'):
                verify(run,run/'run-manifest.json',grid=grid)
            output.write_text(text)
            (run/'scratch/pwscf.save/charge-density.dat').write_text('changed')
            with self.assertRaisesRegex(ValueError,'Changed declared'):
                verify(run,run/'run-manifest.json',grid=grid)


if __name__=='__main__':
    unittest.main()
