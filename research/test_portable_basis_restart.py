from array import array
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from occupation_enrichment import dot
from portable_basis_restart import retained_coefficients,transform,identities,accepted_restart
from portable_restart_sweep import stage


class RitzRestartTest(unittest.TestCase):
    def test_nonsymmetric_transform_preserves_action_and_target(self):
        # A=[[3,1,0],[0,2,0],[0,0,.1]]. Its first two right modes are not orthogonal.
        wr=[3.,2.,.1];wi=[0.,0.,0.];vr=[1.,0.,0.,-1.,1.,0.,0.,0.,1.]
        c,report=retained_coefficients(wr,wi,vr,2,1)
        q=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
        aq=[[3.,0.,0.],[1.,2.,0.],[0.,0.,.1]]
        nq,nu=transform(q,c),transform(aq,c)
        for vector,image in zip(nq,nu):
            expected=[3*vector[0]+vector[1],2*vector[1],.1*vector[2]]
            for a,b in zip(image,expected):self.assertAlmostEqual(a,b,places=14)
        self.assertLess(report['target_coefficient_defect'],1e-14)
        self.assertAlmostEqual(dot(nq[0],nq[1]),0.)
        self.assertAlmostEqual(dot(nq[1],nq[1]),1.)

    def test_conjugate_pair_is_kept_whole(self):
        wr=[2.,1.,1.,.1];wi=[0.,.5,-.5,0.]
        vr=[float(i==j) for j in range(4) for i in range(4)]
        columns,report=retained_coefficients(wr,wi,vr,3,0)
        self.assertEqual(report['indices'],[1,2,3]);self.assertEqual(len(columns),3)
        with self.assertRaisesRegex(ValueError,'splits a conjugate'):
            retained_coefficients(wr,wi,vr,2,0)
        wi[2]=-.4
        with self.assertRaisesRegex(ValueError,'conjugate pair'):
            retained_coefficients(wr,wi,vr,3,0)

    def test_lost_target_and_dependent_modes_rejected(self):
        vr=[1.,0.,0.,0.,1.,0.,0.,0.,1.]
        with self.assertRaisesRegex(ValueError,'discarded'):
            retained_coefficients([3.,2.,1.1],[0.]*3,vr,2,2)
        vr[3:6]=[1.,1e-12,0.]
        with self.assertRaisesRegex(ValueError,'Ill-conditioned'):
            retained_coefficients([3.,2.,.1],[0.]*3,vr,2,0)

    def test_persisted_restart_context_and_payload_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);meta=root/'basis.meta';payload=root/'basis.bin'
            context='a'*64
            meta.write_text('tc-basis-v1\n135880 16\n2.0\n'+context+'\n100 10 10 2 66867 67940\n')
            payload.write_bytes(array('d',[1.]).tobytes());(root/'next.meta').write_text('16\n')
            r=dict(schema='portable-ritz-restart-v1',status='PASS',retained_columns=16,
                trial_columns=16,gram_error=0.,gap_seed_qualified=False,files=[],
                outputs=identities([meta,payload,root/'next.meta']),operator_context_sha256=context,
                beta=2.,parent_manifest={},parent=str(root))
            path=root/'restart-result.json';path.write_text(json.dumps(r))
            with patch('portable_basis_restart.verify_postrun_inputs'):
                self.assertEqual(accepted_restart(root)['beta'],2.)
                payload.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'Changed restart evidence'):accepted_restart(root)
                payload.write_bytes(array('d',[1.]).tobytes())
                r['operator_context_sha256']='b'*64;path.write_text(json.dumps(r))
                with self.assertRaisesRegex(ValueError,'Stale restart metadata'):accepted_restart(root)

    def test_sweep_pins_restart_and_rejects_noncontiguous_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);basis=base/'basis';basis.mkdir()
            for name in ('native.in','restart-result.json'):(basis/name).write_text('fixture')
            r=dict(files=[],outputs=identities([basis/'native.in']),geometry='geometry',z_directory='z',
                operator_context_sha256='a'*64,parent_manifest=dict(command=[
                    '/usr/bin/make','-f',str(Path(__file__).parent/'portable_gap/basis_enrichment.mk'),
                    'RESEARCH=x','QE_ROOT=x','NATIVE_INPUT=old','enrich-basis']))
            with patch('portable_restart_sweep.accepted_restart',return_value=r):
                first=stage(basis,base/'first',1,16384)
                self.assertEqual(first['old_columns'],16)
                self.assertEqual(first['command'][-2],'NATIVE_INPUT='+str(base/'first/native.in'))
                parent=({**first,'context_sha256':'b'*64},{'completed':16384},[])
                with patch('portable_restart_sweep.parent',return_value=parent):
                    with self.assertRaisesRegex(ValueError,'Stale or noncontiguous'):
                        stage(basis,base/'second',16385,32768,base/'first')
