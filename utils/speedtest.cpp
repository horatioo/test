#include <stdio.h>
#include <math.h>
#include <time.h>
#include "emdata.h"
#include "util.h"

using namespace EMAN;

#define CPS	(CLOCKS_PER_SEC)


int main(int argc, char *argv[])
{
    int SIZE = 96;
    int NTT = 500;
 
    int slow = 0;
    int low = 0;
    int big = 0;
    int newali = 0;

    if (argc > 1) {
		if (Util::sstrncmp(argv[1], "slowest"))
			slow = 2;
		else if (Util::sstrncmp(argv[1], "slow"))
			slow = 1;
		else if (Util::sstrncmp(argv[1], "best"))
			slow = 3;
		else if (Util::sstrncmp(argv[1], "low"))
			low = 1;
		else if (Util::sstrncmp(argv[1], "refine"))
			newali = 1;
		else if (Util::sstrncmp(argv[1], "big"))
			big = 1;
    }

    printf("This could take a few minutes. Please be patient.\n");
    if (big) {
		NTT = 100;
		SIZE = 320;
    }


    printf("Initializing\n");
    EMData pat;
    pat.set_size(SIZE, SIZE, 1);
    float *d = pat.get_data();

    for (int i = -SIZE / 2; i < SIZE / 2; i++) {
		for (int j = -SIZE / 2; j < SIZE / 2; j++) {
			d[(i + SIZE / 2) + (j + SIZE / 2) * SIZE] =
				-3.0f * exp(-Util::square((fabs((float)i) + fabs((float)j))) / 10.0f) +
				exp(-Util::square((fabs((float)i) + fabs((float)j) / 2.0f)) / 100.0f) *
				(abs(i) < 2 ? 2.0f : 1.0f);
		}
    }
    pat.done_data();
    pat.filter("NormalizeCircleMean");
    pat.filter("MaskSharp", Dict("outer_radius", pat.get_xsize()/2));

    EMData *data[5000];
    
    for (int i = 0; i < NTT; i++) {
		data[i] = pat.copy(false);
		float *d = data[i]->get_data();

		for (int j = 0; j < SIZE * SIZE; j++) {
			d[j] += Util::get_gauss_rand(0, 1.0);
		}
		data[i]->done_data();
		data[i]->filter("NormalizeCircleMean");
		data[i]->filter("MaskSharp", Dict("outer_radius", data[i]->get_xsize()/2));
	
		if (i < 5) {
			data[i]->write_image("speed.hed", i, EMUtil::IMAGE_IMAGIC);
		}
    }


    if (low) {
		printf("Low level tests starting. Please note that compiling with optimization may invalidate certain tests. Also note that overhead is difficult to compensate for, so in most cases it is not dealt with.\n");
	
		float t1 = (float) clock();
		for (float fj = 0; fj < 500.0; fj += 1.0) {
			for (int i = 0; i < NTT / 2.0; i += 1)
				data[i]->dot(data[i + NTT / 2]);
		}
	
		float t2 = (float) clock();
		float ti = (t2 - t1) / (float) CPS;
		printf("Baseline 1: %d, %d x %d dot()s in %1.1f sec  %1.1f/sec-> ~%1.2f mflops\n",
			   500 * NTT / 2, SIZE, SIZE, ti, 500 * NTT / (2.0 * ti),
			   SIZE * SIZE * 4 * 500.0 * NTT / (1000000.0 * ti));

		t1 = (float) clock();
		for (float fj = 0; fj < 500.0; fj += 1.0) {
			for (float fi = 0; fi < NTT / 2.0; fi += 1.0)
				data[1]->dot(data[12]);
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 1a: %d, %d x %d optimized cached dot()s in %1.1f s %1.1f/s-> ~%1.2f mflops\n",
			   500 * NTT / 2, SIZE, SIZE, ti, 500 * NTT / (2.0 * ti),
			   SIZE * SIZE * 4 * 500.0 * NTT / (1000000.0 * ti));
	
		t1 = (float) clock();
		for (int j = 0; j < 500; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				Dict d;
				d["keepzero"] = 1;
				data[i]->cmp("Variance", data[i + NTT / 2], d);
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 2: %d, %d x %d lcmp()s in %1.1f sec   %1.1f/sec\n", 500 * NTT / 2, SIZE,
			   SIZE, ti, 500 * NTT / (2.0 * ti));

		t1 = (float) clock();
		for (int j = 0; j < 100; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				Dict params;
				data[i]->cmp("Phase", data[i + NTT / 2], params);
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 3: %d, %d x %d pcmp()s in %1.1f sec  %1.1f/sec\n", 100 * NTT / 2, SIZE,
			   SIZE, ti, 100 * NTT / (2.0 * ti));

		t1 = (float) clock();
		for (int j = 0; j < 100; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				Dict params;
				data[i]->cmp("FRC", data[i + NTT / 2], params);
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 4: %d, %d x %d fscmp()s in %1.1f sec  %1.1f/sec\n", 100 * NTT / 2, SIZE,
			   SIZE, ti, 100 * NTT / (2.0 * ti));

		t1 = (float) clock();
		for (int j = 0; j < 500; j++) {
			for (int i = 0; i < NTT / 2; i++)
				data[i]->filter("AbsoluateValue");
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5a: %d, %d x %d fabs in %1.1f sec -> ~%1.2f mfabs/sec\n", 500 * NTT / 2,
			   SIZE, SIZE, ti, SIZE * SIZE * 500.0 * NTT / (1000000.0 * ti));

		t1 = (float) clock();
		for (int j = 0; j < 100; j++) {
			for (int i = 0; i < NTT / 2; i++)
				data[i]->filter("ValueSqrt");
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5b: %d, %d x %d sqrts in %1.1f sec -> ~%1.2f msqrt/sec\n", 100 * NTT / 2,
			   SIZE, SIZE, ti, SIZE * SIZE * 100.0 * NTT / (1000000.0 * ti));

		d = data[0]->get_data();
		t1 = (float) clock();
		for (int j = 0; j < 100; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				for (int k = 0; k < SIZE * SIZE; k++)
					sqrt(d[k]);
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5c: %d, %d x %d sqrts in %1.1f sec -> ~%1.2f msqrt/sec (cached)\n",
			   100 * NTT / 2, SIZE, SIZE, ti, SIZE * SIZE * 100.0 * NTT / (1000000.0 * ti));
		data[0]->done_data();

		d = data[0]->get_data();
		t1 = (float) clock();
		for (int j = 0; j < 100; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				for (int k = 0; k < SIZE * SIZE; k++)
					cos(d[k]);
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5d: %d, %d x %d cos in %1.1f sec -> ~%1.2f mcos/sec (cached)\n",
			   100 * NTT / 2, SIZE, SIZE, ti, SIZE * SIZE * 100.0 * NTT / (1000000.0 * ti));
		data[0]->done_data();

		d = data[0]->get_data();
		t1 = (float) clock();
		for (int j = 0; j < 100; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				for (int k = 0; k < SIZE * SIZE - 1; k++)
					hypot(d[k], d[k + 1]);
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5e: %d, %d x %d hypot in %1.1f sec -> ~%1.2f mhypot/sec (cached)\n",
			   100 * NTT / 2, SIZE, SIZE, ti, SIZE * SIZE * 100.0 * NTT / (1000000.0 * ti));
		data[0]->done_data();

		d = data[0]->get_data();
		t1 = (float) clock();
		for (int j = 0; j < 1000; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				for (int k = 0; k < SIZE * SIZE - 1; k++) {
					float f = d[k] * d[k + 1];
					f = f + f;
				}
			}
		}
	
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5f: %d, %d x %d mult in %1.1f sec -> ~%1.2f mmult/sec (cached)\n",
			   100 * NTT / 2, SIZE, SIZE, ti, SIZE * SIZE * 1000.0 * NTT / (1000000.0 * ti));
		data[0]->done_data();

		d = data[0]->get_data();
		t1 = (float) clock();
		for (int j = 0; j < 500; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				for (int k = 0; k < SIZE * SIZE - 1; k++) {
					float a = d[k] / d[k + 1];
					a = a + a;
				}
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5g: %d, %d x %d div in %1.1f sec -> ~%1.2f mdiv/sec (cached)\n",
			   100 * NTT / 2, SIZE, SIZE, ti, SIZE * SIZE * 500.0 * NTT / (1000000.0 * ti));
		data[0]->done_data();

		d = data[0]->get_data();
		t1 = (float) clock();
		for (int j = 0; j < 500; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				for (int k = 0; k < SIZE * SIZE - 1; k++) {
					float f = fabs(d[k]);
					f = f + f;
				}
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5h: %d, %d x %d fabs in %1.1f sec -> ~%1.2f fabs/sec (cached)\n",
			   100 * NTT / 2, SIZE, SIZE, ti, SIZE * SIZE * 500.0 * NTT / (1000000.0 * ti));
		data[0]->done_data();

		d = data[0]->get_data();
		t1 = (float) clock();
		for (int j = 0; j < 500; j++) {
			for (int i = 0; i < NTT / 2; i++) {
				for (int k = 0; k < SIZE * SIZE - 1; k++) {
					atan2(d[k], d[k + 1]);
					hypot(d[k], d[k + 1]);
				}
			}
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 5i: %d, %d x %d ri2ap in %1.1f sec -> ~%1.2f ri2ap/sec (cached)\n",
			   100 * NTT / 2, SIZE, SIZE, ti, SIZE * SIZE * 500.0 * NTT / (1000000.0 * ti));

		data[0]->done_data();
		t1 = (float) clock();
	
		for (int i = 0; i < NTT * 100; i++) {
			EMData *cp = data[i % NTT]->copy(false);
			cp->mean_shrink(2);
			delete cp;
			cp = 0;
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 6:  %1.1f sec %f meanshrink x 2/sec\n", ti, NTT * 100.0 / ti);

		EMData *d1a = data[0]->copy(false);
		t1 = (float) clock();

		for (int i = 0; i < NTT * 1000; i++) {
			d1a->do_fft();
			d1a->update();
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 7:  %1.1f sec %f ffts/sec\n", ti, NTT * 1000 / ti);
	
		d1a = d1a->copy();
		t1 = (float) clock();

		for (int i = 0; i < NTT * 1000; i++) {
			d1a->translate(-1, -3, 0);
		}
		t2 = (float) clock();
		ti = (t2 - t1) / (float) CPS;
		printf("Baseline 8:  %1.1f sec   %f translates/sec\n", ti, NTT * 1000 / ti);

		return 0;
    }

    
    EMData *tmp = 0;
    float t1 = (float) clock();
    for (int i = 0; i < 3; i++) {
		for (int j = 5; j < (slow == 2 ? NTT / 10 : NTT); j++) {
			if (slow == 2) {
				Dict d;
				d["flip"] = (EMData*)0;
				d["maxshift"] = SIZE/8;
				tmp = data[i]->align("RTFSlowest", data[j], d);
			}
			else if (slow == 3) {
				tmp = data[i]->align("RTFBest", data[j],
									 Dict("flip", (EMData*)0,"maxshift", SIZE/8));
			}
			else if (slow == 1) {
				Dict d;
				d["flip"] = (EMData*)0;
				d["maxshift"] = SIZE/8;
				tmp = data[i]->align("RTFSlow", data[j], d);
			}
			else if (newali == 1) {
				tmp = data[i]->align("RotateTranslateFlip", data[j], Dict());
				tmp->align("Refine", data[j], Dict());
			}
			else {
				tmp = data[i]->align("RotateTranslateFlip", data[j], Dict());
			}
	    
			delete tmp;
			if (j % 10 == 0) {
				putchar('.');
				fflush(stdout);
			}
		}
		putchar('\n');
    }
    float t2 = (float) clock();

    float ti = (t2 - t1) / (float) CPS;
    if (slow == 2)
		ti *= 10.0;
    if (!big && !slow && !newali) {
		printf("\nFor comparison (note these numbers may change from release to release)\n");
		printf("* - denotes old values which may be 25%% higher than the current version\n");
		printf("A  250Mhz R10k Octane has a SF of 180\n");
		printf("A  PIII 800 has a sf of ~390\n");
		printf("An Athlon 1.4ghz has a sf of 580\n");
		printf
			("A Xeon 2600mhz on a 4-way shared memory machine with all processors active has a sf of 380 *\n");
		printf
			("A Xeon 2600mhz on a 4-way shared memory machine with 2 processors active has a sf of 400 *\n");
		printf("A P4 3.2 Ghz with dual channel pc2700 ram has a sf of 800 (*?)\n");
		printf("An Athlon XP2800+ (2133mhz) with gcc3.2 and FFTWGEL has a sf of 1100\n");
		printf("An Athlon64 3000 (2000mhz) with gcc3.2, FFTWGEL and 2.4 kernel has a sf of 1050\n");
		printf("An Athlon64 3200 (2000mhz) 32-bit with FFTWGEL and 2.6 kernel has a sf of 1350\n");
		printf("An Athlon64 3200 (2000mhz) 64-bit has a sf of 1520\n");
		printf("\nYour machines speed factor = %1.1f\n", 25000.0 / ti);
		printf("\n\nThis repesents %1.2f RTFAligns/sec\n",
			   3.0 * ((slow == 2 ? NTT / 10 : NTT) - 5) / ti);
    }
    else if (big && !slow) {
		printf("\nYour machines speed factor = %1.1f\n", 72000.0 / ti);
    }
    else {
		printf("\nYour machines speed factor on this test = %1.1f\n", 25000.0 / ti);
    }

    return 0;
}
       
    
